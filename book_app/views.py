from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from .models import Book, Order, OrderItem, Cart, CartItem, Wishlist
from .forms import SimpleUserCreationForm, BookForm

# =========================
# PUBLIC PAGES
# =========================
def home(request):  # show home page
    return render(request, 'book_app/home.html')


@login_required
def book_list(request):  # show all books
    books = Book.objects.all()
    return render(request, 'book_app/book_list.html', {'books': books})


@login_required
def book_detail(request, id):  # single book detail
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})


# =========================
# AUTHENTICATION
# =========================
def signup(request):  # register new user
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():  # valid form → save user
            form.save()
            return redirect('login')
    else:
        form = SimpleUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):  # login user
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:  # correct credentials → login
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")  # show error

    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):  # logout user
    logout(request)
    return redirect('home')


# =========================
# BOOK CRUD (STAFF)
# =========================
@login_required
def add_book(request):  # add new book
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():  # valid → save
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_app/add_book.html', {'form': form})


# =========================
# DASHBOARD (STAFF ONLY)
# =========================
def staff_required(user):  # staff only
    return user.is_staff


@login_required
@user_passes_test(staff_required)
def dashboard(request):  # show dashboard
    books = Book.objects.all()
    orders = Order.objects.all().order_by('-ordered_at')
    return render(request, 'dashboard/dashboard.html', {'books': books, 'orders': orders})


@login_required
@user_passes_test(staff_required)
def manage_books(request):  # manage books
    books = Book.objects.all()
    return render(request, 'dashboard/manage_books.html', {'books': books})


@login_required
@user_passes_test(staff_required)
def edit_book(request, id):  # edit book
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()  # save changes
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)
    return render(request, 'dashboard/edit_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def delete_book(request, id):  # delete book
    book = get_object_or_404(Book, id=id)
    book.delete()  # remove from DB
    return redirect('manage_books')


# =========================
# ORDER STATUS UPDATE
# =========================
@login_required
@user_passes_test(staff_required)
def update_order_status(request, order_id):  # change order status
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = request.POST.get('status')  # update status
        order.save()  # save
    return redirect('dashboard')


# =========================
# PAYMENT (SIMULATION)
# =========================
@login_required
def buy_book(request, book_id):  # single book buy
    book = get_object_or_404(Book, id=book_id)
    Order.objects.create(user=request.user, book=book, price=book.price)  # create order
    return redirect('payment_success')


@login_required
def payment_success(request):  # payment success page
    return render(request, 'book_app/payment_success.html')


# =========================
# CART SYSTEM
# =========================
@login_required
def add_to_cart(request, book_id):  # add book to cart
    book = get_object_or_404(Book, id=book_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)  # get or create cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1  # increase quantity if exists
        cart_item.save()
    return redirect('view_cart')


@login_required
def view_cart(request):  # show cart
    cart = Cart.objects.filter(user=request.user).first()
    items = cart.items.all() if cart else []
    total = sum(item.book.price * item.quantity for item in items)  # calculate total
    return render(request, 'book_app/cart.html', {'cart': cart, 'items': items, 'total': total})


@login_required
def increase_quantity(request, item_id):  # + button
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity += 1
    item.save()
    return redirect('view_cart')


@login_required
def decrease_quantity(request, item_id):  # − button
    item = get_object_or_404(CartItem, id=item_id)
    item.quantity -= 1
    if item.quantity <= 0:
        item.delete()  # remove if zero
    else:
        item.save()
    return redirect('view_cart')


# =========================
# CHECKOUT
# =========================
@login_required
def checkout(request):  # checkout page
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        return redirect('view_cart')

    cart_items = cart.items.all()
    total = sum(item.book.price * item.quantity for item in cart_items)  # total price

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_price=total)  # create order
        for item in cart_items:  # move items to order
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )
        cart_items.delete()  # clear cart
        return redirect('order_success')

    return render(request, 'book_app/checkout.html', {'cart_items': cart_items, 'total': total})


@login_required
def order_success(request):  # simple order confirmation
    return render(request, 'book_app/order_success.html')


# =========================
# WISHLIST SYSTEM
# =========================

@login_required
def add_to_wishlist(request, book_id):  # add book to wishlist
    book = get_object_or_404(Book, id=book_id)

    # create wishlist item if not already added
    Wishlist.objects.get_or_create(
        user=request.user,
        book=book
    )

    return redirect('wishlist')  # go to wishlist page


@login_required
def remove_from_wishlist(request, book_id):  # remove book from wishlist
    Wishlist.objects.filter(
        user=request.user,
        book_id=book_id
    ).delete()

    return redirect('wishlist')


@login_required
def wishlist(request):  # show user's wishlist
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'book_app/wishlist.html', {'items': items})
