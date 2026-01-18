from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.core.paginator import Paginator   # pagination logic
from django.db.models import Q                # search multiple fields

from .models import Book, Order, OrderItem, Cart, CartItem, Wishlist
from .forms import SimpleUserCreationForm, BookForm, AddressForm


# =========================
# PUBLIC PAGES
# =========================
def home(request):
    # show home page
    return render(request, 'book_app/home.html')


def book_list(request):
    # --------------------------
    # 1️⃣ Search
    # --------------------------
    query = request.GET.get("q")
    books = Book.objects.all()
    if query:
        # search by title OR author (case-insensitive)
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )

    # --------------------------
    # 2️⃣ Ordering (optional)
    # --------------------------
    order = request.GET.get("order")
    if order == "price_low":
        books = books.order_by("price")        # Price low → high
    elif order == "latest":
        books = books.order_by("-created_at")  # Latest first
    elif order == "alpha":
        books = books.order_by("title")        # Alphabetical

    # --------------------------
    # 3️⃣ Filtering (optional)
    # --------------------------
    category = request.GET.get("category")
    author_filter = request.GET.get("author")
    availability = request.GET.get("availability")

    if category:
        books = books.filter(category__name=category)  # filter by category name
    if author_filter:
        books = books.filter(author__icontains=author_filter)  # filter by author
    if availability == "in_stock":
        books = books.filter(stock__gt=0)  # only books with stock > 0

    # --------------------------
    # 4️⃣ Pagination
    # --------------------------
    paginator = Paginator(books, 8)  # 8 books per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --------------------------
    # 5️⃣ Render template
    # --------------------------
    return render(request, "book_app/book_list.html", {
        "page_obj": page_obj,       # paginated books
        "query": query,             # search query
        "order": order,             # ordering
        "category": category,       # filter category
        "author": author_filter,    # filter author
        "availability": availability
    })


def book_detail(request, id):
    # show single book details
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})


# =========================
# AUTHENTICATION
# =========================
def signup(request):
    # prevent logged-in users from signing up again
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # create new user
            return redirect('login')
    else:
        form = SimpleUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    # prevent logged-in users from logging in again
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # login user
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):
    # logout user
    logout(request)
    return redirect('home')


# =========================
# STAFF CHECK
# =========================
def staff_required(user):
    # allow only staff users
    return user.is_staff


# =========================
# BOOK CRUD (STAFF ONLY)
# =========================
@login_required
@user_passes_test(staff_required)
def add_book(request):
    # staff adds new book
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()

    return render(request, 'book_app/add_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def edit_book(request, id):
    # admin edits book
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'dashboard/edit_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def delete_book(request, id):
    # admin deletes book
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('manage_books')


# =========================
# DASHBOARD (STAFF ONLY)
# =========================
@login_required
@user_passes_test(staff_required)
def dashboard(request):
    # admin dashboard
    books = Book.objects.all()
    orders = Order.objects.all().order_by('-ordered_at')
    return render(request, 'dashboard/dashboard.html', {'books': books, 'orders': orders})


@login_required
@user_passes_test(staff_required)
def manage_books(request):
    # admin manages books
    books = Book.objects.all()
    return render(request, 'dashboard/manage_books.html', {'books': books})


@login_required
@user_passes_test(staff_required)
def update_order_status(request, order_id):
    # admin updates order status
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
    # show specific order details
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'dashboard/order_detail.html', {'order': order})


# =========================
# CART SYSTEM
# =========================
@login_required
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []
    total = sum(item.book.price * item.quantity for item in items)
    return render(request, 'book_app/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
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


# =========================
# CHECKOUT (WITH ADDRESS FORM)
# =========================
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('view_cart')

    cart_items = cart.items.all()
    total = sum(item.book.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

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

            cart_items.delete()  # clear cart after order
            return redirect('order_success')
    else:
        form = AddressForm()

    return render(request, 'book_app/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form
    })


@login_required
def order_success(request):
    # order confirmation page
    return render(request, 'book_app/order_success.html')


# =========================
# USER ORDERS
# =========================
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'book_app/my_orders.html', {'orders': orders})


# =========================
# WISHLIST SYSTEM
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
