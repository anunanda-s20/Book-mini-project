from django.shortcuts import render, redirect, get_object_or_404  # render template, redirect page, safely get object
from django.contrib.auth.decorators import login_required, user_passes_test  # protect views
from django.contrib.auth import authenticate, login, logout  # authentication functions
from django.contrib import messages  # show success/error messages
from django.core.paginator import Paginator  # pagination
from django.db.models import Q  # advanced search queries

from .models import Book, Order, OrderItem, Cart, CartItem, Wishlist, Address, Category # models
from .forms import SimpleUserCreationForm, BookForm, AddressForm, EditProfileForm # forms


# 1️.HOME PAGE
# =========================
def home(request):

    hero_range = range(1, 4)  # slider range (1,2,3)

    categories = Category.objects.exclude(title__iexact="Book Accessories")  # exclude accessories category

    popular_books = Book.objects.filter(
        is_active=True,
        product_type='book'
    )[:]  # all active books

    new_arrivals = Book.objects.filter(
        is_active=True,
        product_type='book'
    ).order_by('-created_at')[:4]  # latest 4 books

    book_essentials = Book.objects.filter(
        is_active=True,
        product_type='accessory'
    ).order_by('-created_at')[:4]  # latest 4 accessories

    return render(request, 'book_app/home.html', {
        "hero_range": hero_range,
        "categories": categories,
        "popular_books": popular_books,
        "new_arrivals": new_arrivals,
        "book_essentials": book_essentials,
    })



# 2️.BOOK LIST PAGE
# =========================
def book_list(request):

    books = Book.objects.filter(
        is_active=True,
        product_type='book'
    )  # all active books

    query = request.GET.get("q", "")  # search keyword
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )  # search by title or author

    availability = request.GET.get("availability")
    if availability == "in_stock":
        books = books.filter(stock__gt=0)  # only books in stock

    order = request.GET.get("order")  # sorting option
    if order == "price_low":
        books = books.order_by("price")
    elif order == "latest":
        books = books.order_by("-created_at")
    elif order == "alpha":
        books = books.order_by("title")

    paginator = Paginator(books, 10)  # 10 books per page
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "book_app/book_list.html", {
        "page_obj": page_obj,
        "query": query,
        "order": order,
        "availability": availability
    })



# 3️. BOOK DETAIL
# =========================
def book_detail(request, id):

    book = get_object_or_404(Book, id=id, is_active=True)  # get book safely

    suggested_books = Book.objects.filter(
        is_active=True,
        product_type='book'
    ).exclude(id=id)[:4]  # 4 suggested books

    book_essentials = Book.objects.filter(
        is_active=True,
        product_type='accessory'
    )[:4]  # 4 accessories

    is_wishlisted = (
        Wishlist.objects.filter(user=request.user, book=book).exists()
        if request.user.is_authenticated else False
    )  # check if book in wishlist

    context = {
        'book': book,
        'is_wishlisted': is_wishlisted,
        'suggested_books': suggested_books,
        'book_essentials': book_essentials,
    }

    return render(request, 'book_app/book_detail.html', context)



# 4.AUTHENTICATION
# =========================
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')  # already logged in

    form = SimpleUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()  # create user
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)  # check credentials
        if user:
            login(request, user)  # log user in
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):
    logout(request)  # log out
    messages.success(request, "Logged out successfully")
    return redirect('home')



# 5.STAFF CHECK
# =========================
def staff_required(user):
    return user.is_staff  # allow only staff users



# 6.BOOK CRUD (STAFF)
# =========================
@login_required
@user_passes_test(staff_required)
def add_book(request):
    form = BookForm(request.POST or None)  # book form
    if request.method == "POST" and form.is_valid():
        form.save()  # save new book
        return redirect('manage_books')
    return render(request, 'book_app/add_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)  # get book to edit
    form = BookForm(request.POST or None, instance=book)  # bind existing book
    if request.method == "POST" and form.is_valid():
        form.save()  # update book
        return redirect('manage_books')
    return render(request, 'dashboard/edit_book.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def delete_book(request, id):
    get_object_or_404(Book, id=id).delete()  # delete book
    messages.success(request, "Book deleted successfully")
    return redirect('manage_books')



# 7.DASHBOARD (STAFF)
# =========================
@login_required
@user_passes_test(staff_required)
def dashboard(request):
    books = Book.objects.all()  # all books
    orders_list = Order.objects.all().order_by('-created_at')  # all orders
    paginator = Paginator(orders_list, 10)  # paginate orders
    orders = paginator.get_page(request.GET.get('page'))

    context = {
        'books': books,
        'orders': orders,
        'total_books': books.count(),  # total book count
        'total_orders': orders_list.count(),  # total orders
        'total_revenue': sum(
            o.total_price for o in orders_list
            if o.status in ['paid', 'shipped', 'delivered']
        ),  # revenue from completed orders
        'pending_orders': orders_list.filter(status='pending').count(),
        'delivered_orders': orders_list.filter(status='delivered').count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@user_passes_test(staff_required)
def manage_books(request):
    query = request.GET.get('q')  # search keyword
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )  # search books
    return render(request, 'dashboard/manage_books.html', {'books': books, 'query': query})


@login_required
@user_passes_test(staff_required)
def dashboard_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)  # get order

    order_items = [
        {
            'book': i.book,
            'quantity': i.quantity,
            'price': i.price,
            'subtotal': i.quantity * i.price
        }
        for i in order.items.all()
    ]  # prepare order items

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status  # update order status
            order.save()
            messages.success(request, "Order status updated")
        return redirect('dashboard')

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'order_items': order_items
    })



# 8.CART
# =========================
@login_required
def add_to_cart(request, book_id):

    book = get_object_or_404(Book, id=book_id)  # get book

    if book.stock <= 0:
        messages.error(request, "Out of stock")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart, _ = Cart.objects.get_or_create(user=request.user)  # get or create cart
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)  # get or create item

    if not created and item.quantity < book.stock:
        item.quantity += 1  # increase quantity
        item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()  # get user cart
    items = cart.items.all() if cart else []  # cart items
    total = sum(i.book.price * i.quantity for i in items)  # calculate total
    return render(request, 'book_app/cart.html', {'items': items, 'total': total})


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
        item.delete()  # remove item if quantity 0
    else:
        item.save()
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    return redirect('view_cart')




# 9.CHECKOUT
# =========================
@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()  # get user's cart
    if not cart:
        return redirect('view_cart')  # if no cart

    cart_items = cart.items.all()  # all cart items
    total = sum(i.book.price * i.quantity for i in cart_items)  # total price

    address = Address.objects.filter(user=request.user).first()  # get address
    if not address:
        messages.error(request, "Add address first")
        return redirect('my_profile')

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total,
            status='pending'
        )  # create order

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )  # create order items

            item.book.stock -= item.quantity  # reduce stock
            item.book.save()

        cart_items.delete()  # clear cart after order
        return redirect('order_success')

    return render(request, 'book_app/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'address': address
    })



# 10.USER ORDERS
# =========================
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # user's orders
    return render(request, 'book_app/my_orders.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)  # get user's order

    if order.status not in ['pending', 'paid']:
        messages.error(request, "Cannot cancel now")
        return redirect('my_orders')

    order.status = 'cancelled'  # update status
    order.save()

    for item in order.items.all():
        item.book.stock += item.quantity  # restore stock
        item.book.save()

    messages.success(request, "Order cancelled")
    return redirect('my_orders')



# 11.WISHLIST
# =========================
@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)  # get wishlist items
    return render(request, 'book_app/wishlist.html', {'items': items})


@login_required
def add_to_wishlist(request, book_id):
    Wishlist.objects.get_or_create(
        user=request.user,
        book=get_object_or_404(Book, id=book_id)
    )  # add book to wishlist
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(
        user=request.user,
        book_id=book_id
    ).delete()  # remove from wishlist
    return redirect('wishlist')



# 12.PROFILE
# =========================
@login_required
def my_profile(request):
    profile = request.user.userprofile  # get user's profile
    return render(request, 'book_app/my_profile.html', {
        'user': request.user,
        'profile': profile
    })



# 13.ADDRESS
# =========================
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)  # user's addresses
    return render(request, 'book_app/address_list.html', {'addresses': addresses})


@login_required
def add_address(request):
    form = AddressForm(request.POST or None)  # address form
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)  # don't save yet
        address.user = request.user  # assign user
        address.save()  # save address
        return redirect('address_list')
    return render(request, 'book_app/add_address.html', {'form': form})



# 14.PROFILE EDIT
# =========================
@login_required
def edit_profile(request):
    user = request.user  # current user
    profile = user.userprofile  # related profile

    form = EditProfileForm(request.POST or None, instance=profile)

    if request.method == "POST" and form.is_valid():
        form.save()  # save profile changes

        if request.POST.get('username'):
            user.username = request.POST.get('username')  # update username

        if request.POST.get('email'):
            user.email = request.POST.get('email')  # update email

        user.save()
        messages.success(request, "Profile updated")
        return redirect('my_profile')

    return render(request, 'book_app/edit_profile.html', {
        'form': form,
        'user': user
    })



# 15.ORDER SUCCESS
# =========================
@login_required
def order_success(request):
    return render(request, 'book_app/order_success.html')  # success page



# 16.ABOUT PAGE
# =========================
def about(request):
    return render(request, 'book_app/about.html')  # static about page


# =========================
# 17.CATEGORY PAGE
# =========================
def category_books(request, category_id):

    category = get_object_or_404(Category, id=category_id)  # get category

    books = Book.objects.filter(
        category=category,
        is_active=True,
        product_type='book'
    )  # books in this category

    return render(request, 'book_app/category_books.html', {
        'category': category,
        'books': books
    })
