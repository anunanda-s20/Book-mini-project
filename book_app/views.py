from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import (
    Book, Order, OrderItem, Cart, CartItem,
    Wishlist, Address, UserProfile
)
from .forms import SimpleUserCreationForm, BookForm, AddressForm


# =========================
# PUBLIC PAGES
# =========================
def home(request):
    return render(request, 'book_app/home.html')


def book_list(request):
    books = Book.objects.all()

    query = request.GET.get("q", "")
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))

    availability = request.GET.get("availability", "")
    if availability == "in_stock":
        books = books.filter(stock__gt=0)

    order = request.GET.get("order", "")
    if order == "price_low":
        books = books.order_by("price")
    elif order == "latest":
        books = books.order_by("-created_at")
    elif order == "alpha":
        books = books.order_by("title")

    paginator = Paginator(books, 8)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "book_app/book_list.html", {
        "page_obj": page_obj,
        "query": query,
        "order": order,
        "availability": availability,
    })


def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, book=book).exists()
    return render(request, 'book_app/book_detail.html', {
        'book': book,
        'is_wishlisted': is_wishlisted
    })


# =========================
# AUTHENTICATION
# =========================
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = SimpleUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')


# =========================
# STAFF CHECK
# =========================
def staff_required(user):
    return user.is_staff


# =========================
# BOOK CRUD (STAFF)
# =========================
@login_required
@user_passes_test(staff_required)
def add_book(request):
    form = BookForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('book_list')
    return render(request, 'book_app/add_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)
    form = BookForm(request.POST or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('manage_books')
    return render(request, 'dashboard/edit_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def delete_book(request, id):
    get_object_or_404(Book, id=id).delete()
    return redirect('manage_books')


# =========================
# DASHBOARD (STAFF)
# =========================
@login_required
@user_passes_test(staff_required)
def dashboard(request):
    return render(request, 'dashboard/dashboard.html', {
        'books': Book.objects.all(),
        'orders': Order.objects.all().order_by('-created_at')
    })


@login_required
@user_passes_test(staff_required)
def manage_books(request):
    return render(request, 'dashboard/manage_books.html', {
        'books': Book.objects.all()
    })


@login_required
@user_passes_test(staff_required)
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, "Order status updated successfully")

        # ✅ FIX: redirect to dashboard (NOT same ID page)
        return redirect('dashboard')

    return render(request, 'dashboard/order_detail.html', {'order': order})


# =========================
# CART
# =========================
@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.stock <= 0:
        messages.error(request, "Out of stock")
        return redirect('book_list')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    if not created and item.quantity < book.stock:
        item.quantity += 1
        item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []
    total = sum(i.book.price * i.quantity for i in items)

    return render(request, 'book_app/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if item.quantity < item.book.stock:
        item.quantity += 1
        item.save()
    return redirect('view_cart')


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity -= 1
    if item.quantity <= 0:
        item.delete()
    else:
        item.save()
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    return redirect('view_cart')


# =========================
# CHECKOUT
# =========================
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('view_cart')

    cart_items = cart.items.all()
    total = sum(i.book.price * i.quantity for i in cart_items)
    address = Address.objects.filter(user=request.user).first()

    if not address:
        messages.error(request, "Add address first")
        return redirect('my_profile')

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total,
            status='pending'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )

            # Reduce stock
            item.book.stock -= item.quantity
            item.book.save()

        cart_items.delete()
        return redirect('order_success')

    return render(request, 'book_app/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'address': address
    })


# =========================
# USER ORDERS
# =========================
@login_required
def my_orders(request):
    return render(request, 'book_app/my_orders.html', {
        'orders': Order.objects.filter(user=request.user).order_by('-created_at')
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'book_app/order_detail.html', {'order': order})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status not in ['pending', 'paid']:
        messages.error(request, "Cannot cancel now")
        return redirect('my_orders')

    order.status = 'cancelled'
    order.save()

    for item in order.items.all():
        item.book.stock += item.quantity
        item.book.save()

    messages.success(request, "Order cancelled")
    return redirect('my_orders')


# =========================
# WISHLIST
# =========================
@login_required
def wishlist(request):
    return render(request, 'book_app/wishlist.html', {
        'items': Wishlist.objects.filter(user=request.user)
    })


@login_required
def add_to_wishlist(request, book_id):
    Wishlist.objects.get_or_create(
        user=request.user,
        book=get_object_or_404(Book, id=book_id)
    )
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(user=request.user, book_id=book_id).delete()
    return redirect('wishlist')


# =========================
# PROFILE & ADDRESS
# =========================
@login_required
def my_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'book_app/my_profile.html', {
        'user': request.user,
        'profile': profile
    })


@login_required
def address_list(request):
    return render(request, 'book_app/address_list.html', {
        'addresses': Address.objects.filter(user=request.user)
    })


@login_required
def add_address(request):
    form = AddressForm(request.POST or None)
    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        return redirect('address_list')
    return render(request, 'book_app/add_address.html', {'form': form})


# =========================
# ORDER SUCCESS
# =========================
@login_required
def order_success(request):
    return render(request, 'book_app/order_success.html')
