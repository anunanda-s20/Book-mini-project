from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import Book, Order, OrderItem, Cart, CartItem, Wishlist
from .forms import SimpleUserCreationForm, BookForm


# =========================
# PUBLIC PAGES
# =========================
def home(request):
    # show home page
    return render(request, 'book_app/home.html')


def book_list(request):
    # show all books
    books = Book.objects.all()
    return render(request, 'book_app/book_list.html', {'books': books})


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


# =========================
# DASHBOARD (STAFF ONLY)
# =========================
@login_required
@user_passes_test(staff_required)
def dashboard(request):
    # admin dashboard
    books = Book.objects.all()
    orders = Order.objects.all().order_by('-ordered_at')
    return render(request, 'dashboard/dashboard.html', {
        'books': books,
        'orders': orders
    })


@login_required
@user_passes_test(staff_required)
def manage_books(request):
    # admin manages books
    books = Book.objects.all()
    return render(request, 'dashboard/manage_books.html', {'books': books})


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
# ORDER STATUS UPDATE (STAFF)
# =========================
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


# =========================
# CART SYSTEM
# =========================
@login_required
def add_to_cart(request, book_id):
    # add book to cart
    book = get_object_or_404(Book, id=book_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        book=book
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    # show user cart
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []

    total = sum(item.book.price * item.quantity for item in items)

    return render(request, 'book_app/cart.html', {
        'cart': cart,
        'items': items,
        'total': total
    })


@login_required
def increase_quantity(request, item_id):
    # increase cart item quantity
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )
    item.quantity += 1
    item.save()
    return redirect('view_cart')


@login_required
def decrease_quantity(request, item_id):
    # decrease cart item quantity
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.quantity -= 1
    if item.quantity <= 0:
        item.delete()
    else:
        item.save()

    return redirect('view_cart')


# =========================
# CHECKOUT (BACKEND SAFE – NO UI YET)
# =========================
@login_required
def checkout(request):
    # checkout page
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('view_cart')

    cart_items = cart.items.all()
    total = sum(item.book.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=total,                 # total order price

            # temporary backend-safe values
            shipping_name="Not provided",       # customer name
            shipping_phone="Not provided",      # phone number
            shipping_address="Not provided",    # delivery address
            shipping_city="Not provided",       # city
            shipping_pincode="Not provided"     # pincode
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )

        cart_items.delete()  # clear cart
        return redirect('order_success')

    return render(request, 'book_app/checkout.html', {
        'cart_items': cart_items,
        'total': total
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
    # show logged-in user's orders
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-ordered_at')

    return render(request, 'book_app/my_orders.html', {
        'orders': orders
    })


# =========================
# WISHLIST SYSTEM
# =========================
@login_required
def add_to_wishlist(request, book_id):
    # add book to wishlist
    book = get_object_or_404(Book, id=book_id)
    Wishlist.objects.get_or_create(
        user=request.user,
        book=book
    )
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, book_id):
    # remove book from wishlist
    Wishlist.objects.filter(
        user=request.user,
        book_id=book_id
    ).delete()
    return redirect('wishlist')


@login_required
def wishlist(request):
    # show user's wishlist
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'book_app/wishlist.html', {'items': items})

# =========================
# CHECKOUT (WITH ADDRESS FORM)
# =========================
@login_required
def checkout(request):
    # get user's cart
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('view_cart')  # if cart empty, go back

    cart_items = cart.items.all()
    total = sum(item.book.price * item.quantity for item in cart_items)

    # POST = user submitted the address form
    if request.method == 'POST':
        from .forms import AddressForm  # import here to follow your style
        form = AddressForm(request.POST)
        if form.is_valid():
            # save the address linked to this user
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            # create order with this address
            order = Order.objects.create(
                user=request.user,
                address=address,  # link to address
                total_price=total,
                status='pending',  # default status
            )

            # move cart items to order items
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
        # GET = show empty address form
        from .forms import AddressForm
        form = AddressForm()

    # render checkout page with cart items, total price, and address form
    return render(request, 'book_app/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form
    })


# =========================
# ORDER DETAIL (STAFF ONLY)
# =========================
@login_required
@user_passes_test(staff_required)
def dashboard_order_detail(request, order_id):
    # get the specific order or 404 if not found
    order = get_object_or_404(Order, id=order_id)
    
    # send order to template
    return render(request, 'dashboard/order_detail.html', {'order': order})


@login_required
@user_passes_test(staff_required)
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)  # get the book
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)  # bind form to book
        if form.is_valid():
            form.save()  # save all changes
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)  # show current book data

    return render(request, 'dashboard/edit_book.html', {'form': form})