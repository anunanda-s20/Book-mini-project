from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Book, Order, OrderItem, Cart, CartItem, Wishlist
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
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "book_app/book_list.html", {
        "page_obj": page_obj,
        "query": query,
        "order": order,
        "availability": availability,
    })


def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})


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
    book = get_object_or_404(Book, id=id)
    book.delete()
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


# =========================
# ORDERS (STAFF)
# =========================
@login_required
@user_passes_test(staff_required)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
    return redirect('dashboard')


@login_required
@user_passes_test(staff_required)
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'dashboard/order_detail.html', {'order': order})


# =========================
# CART SYSTEM
# =========================
@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # ❌ Cannot add if out of stock
    if book.stock <= 0:
        messages.error(request, "This book is out of stock!")
        return redirect('book_list')

    # ✅ Get or create user's cart and cart item
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    # 🔼 Only increase quantity if below stock
    if not created:
        if cart_item.quantity < book.stock:
            cart_item.quantity += 1
            cart_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []
    total = sum(item.book.price * item.quantity for item in items)
    return render(request, 'book_app/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    # ✅ Only increase if quantity < stock
    if item.quantity < item.book.stock:
        item.quantity += 1
        item.save()
    else:
        messages.warning(request, "You cannot add more than available stock!")

    return redirect('view_cart')


@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.quantity -= 1
    if item.quantity <= 0:
        item.delete()  # remove item if quantity zero
    else:
        item.save()
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
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
    total = sum(item.book.price * item.quantity for item in cart_items)

    form = AddressForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()

        order = Order.objects.create(user=request.user, address=address, total_price=total)

        for item in cart_items:
            OrderItem.objects.create(order=order, book=item.book,
                                     quantity=item.quantity, price=item.book.price)

        cart_items.delete()
        return redirect('order_success')

    return render(request, 'book_app/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form
    })


@login_required
def order_success(request):
    return render(request, 'book_app/order_success.html')


# =========================
# USER ORDERS
# =========================
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'book_app/my_orders.html', {'orders': orders})


# =========================
# WISHLIST
# =========================
@login_required
def add_to_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(user=request.user, book_id=book_id).delete()
    return redirect('wishlist')


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'book_app/wishlist.html', {'items': items})
