from django.shortcuts import render, redirect, get_object_or_404  # render template, redirect page, safely get object
from django.contrib.auth.decorators import login_required, user_passes_test  # protect views
from django.contrib.auth import authenticate, login, logout  # authentication functions
from django.contrib import messages  # show success/error messages
from django.core.paginator import Paginator  # pagination
from django.db.models import Q  # advanced search queries

from django.views.decorators.csrf import csrf_exempt

import razorpay
from django.conf import settings
from django.http import HttpResponse

from .models import Book, Order, OrderItem, Cart, CartItem, Wishlist, Address, Category, BookImage # models
from .forms import SimpleUserCreationForm, BookForm, AddressForm, EditProfileForm # forms


# 1️.HOME PAGE
# =========================
def home(request):

    hero_range = range(1, 4)  # slider range (1,2,3)

    categories = Category.objects.filter(
    book__product_type='book'
).distinct()  # exclude accessories category

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
    product_type='accessory',
    category__isnull=False
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

    
    # search 
    # Get search keyword from URL (if no keyword, default is empty)
    query = request.GET.get("q", "") 
    # If user entered something in search
    if query:
        books = books.filter( # filter books by title or author
            Q(title__icontains=query) |  # match title (case-insensitive)
            Q(author__icontains=query)   # OR match author (case-insensitive)
        )  # search by title or author


    availability = request.GET.get("availability") # provide available-books
    if availability == "in_stock":
        books = books.filter(stock__gt=0)  # only books in stock

    order = request.GET.get("order")  # sorting option
    if order == "price_low":
        books = books.order_by("price")
    elif order == "latest":
        books = books.order_by("-created_at")
    elif order == "alpha":
        books = books.order_by("title")

    paginator = Paginator(books, 8)  # 10 books per page
    page_obj = paginator.get_page(request.GET.get("page")) # Fetch page number from URL and paginate books accordingly

    return render(request, "book_app/book_list.html", {
        "page_obj": page_obj,
        "query": query,
        "order": order,
        "availability": availability
    }) # returns-paginated result



# =========================
# 3️. BOOK DETAIL
# =========================
def book_detail(request, id):

    # get current book safely
    book = get_object_or_404(Book, id=id, is_active=True)

    # suggested books (exclude current book)
    suggested_books = Book.objects.filter(
        is_active=True,
        product_type='book'
    ).exclude(id=id)[:4]

    # book essentials (exclude-current product )
    book_essentials = Book.objects.filter(
        is_active=True,
        product_type='accessory',
        category__isnull=False
    ).exclude(id=id).order_by('-created_at')[:4]  
    # exclude current product = prevents showing same item again

    # check if current book is in wishlist
    is_wishlisted = (
        Wishlist.objects.filter(user=request.user, book=book).exists()
        if request.user.is_authenticated else False
    )

    # send data to template
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
    if request.user.is_authenticated: # check-current user(already logged-in)-logged-in
        return redirect('home')  

    form = SimpleUserCreationForm(request.POST or None) # form-formdata or emptyform
    if request.method == "POST" and form.is_valid(): # if method-POST and formvalid
        form.save()  
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    # Temporary message if redirected (ONLY ONCE)
    next_page = request.GET.get('next')
    if next_page and not request.session.get('login_message_shown'):
        messages.info(request, "You must log in to continue to the page you wanted.")
        request.session['login_message_shown'] = True

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # remove flag after login
            request.session.pop('login_message_shown', None)

            messages.success(request, f"Welcome back, {user.username}!")

            next_redirect = request.POST.get('next') or 'home'
            return redirect(next_redirect)
        
        messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):
    logout(request)  # removes-session
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
    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        book = form.save()  # save book first

        # Handle multiple images
        images = request.FILES.getlist('images')
        for img in images:
            BookImage.objects.create(book=book, image=img)

        messages.success(request, "Book added successfully.")
        return redirect('manage_books')

    return render(request, 'book_app/add_book.html', {'form': form})



@login_required
@user_passes_test(staff_required)
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)

    if request.method == "POST" and form.is_valid():
        form.save()

        # Handle new images
        images = request.FILES.getlist('images')
        for img in images:
            BookImage.objects.create(book=book, image=img)

        messages.success(request, "Book updated successfully.")
        return redirect('manage_books')

    return render(request, 'dashboard/edit_book.html', {'form': form, 'book': book})


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
    orders = paginator.get_page(request.GET.get('page'))# Fetch page number from URL and paginate books accordingly

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
    query = request.GET.get('q', '')  # get search text
    product_type = request.GET.get('type', '')  # get dropdown value (book/accessory)

    books = Book.objects.all()  # get all items

    # Search filter
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )

    # Product type filter (like admin)
    if product_type == 'book':
        books = books.filter(product_type='book')  # only books
    elif product_type == 'accessory':
        books = books.filter(product_type='accessory')  # only accessories

    return render(request, 'dashboard/manage_books.html', {
        'books': books,
        'query': query,
        'product_type': product_type  # send to template
    })


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



# 8. CART
# =========================

@login_required
def add_to_cart(request, book_id):

    book = get_object_or_404(Book, id=book_id)

    if book.stock <= 0:
        messages.error(request, "Out of stock")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, book=book)

    #  NEW: message for first time add
    if created:
        messages.success(request, f'"{book.title}" added to cart.')

    #  EXISTING LOGIC (UNCHANGED)
    if not created and item.quantity < book.stock:
        item.quantity += 1
        item.save()
        messages.success(request, f'Quantity increased for "{book.title}".')

    #  NEW: stock limit message (ONLY extra check, no logic change)
    elif not created and item.quantity >= book.stock:
        messages.warning(request, "You reached the available stock limit.")

    return redirect('view_cart')



@login_required  # user must be logged in
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()  
    # get current user's cart

    items = cart.items.all() if cart else []  
    # get cart items if cart exists

    total = sum(i.book.price * i.quantity for i in items)  
    # calculate total price

    return render(request, 'book_app/cart.html', {'items': items, 'total': total})
    # display cart page


@login_required
def increase_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    # get cart item of current user

    if item.quantity < item.book.stock:  # check stock limit
        item.quantity += 1  # increase quantity
        item.save()

        messages.success(request, "Quantity increased.")
    else:
        messages.warning(request, "You reached the available stock limit.")

    return redirect('view_cart')



@login_required
def decrease_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    # get cart item of current user

    item.quantity -= 1  # decrease quantity

    if item.quantity <= 0:
        item.delete()  # remove item if quantity is 0
        messages.success(request, "Item removed from cart.")
    else:
        item.save()  # save updated quantity
        messages.success(request, "Quantity decreased.")

    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    get_object_or_404(CartItem, id=item_id, cart__user=request.user).delete()
    # delete selected cart item

    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')




# 9. CHECKOUT
# =========================

@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()

    if not cart:
        return redirect('view_cart')

    cart_items = cart.items.all()

    if not cart_items:
        return redirect('view_cart')

    total = sum(i.book.price * i.quantity for i in cart_items)

    selected_address_id = request.session.get('selected_address_id')
    address = None

    if selected_address_id:
        address = Address.objects.filter(
            id=selected_address_id,
            user=request.user
        ).first()

    if not address:
        address = Address.objects.filter(user=request.user).order_by('-id').first()

        if address:
            request.session['selected_address_id'] = address.id

    if not address:
        messages.warning(request, "🚚 Please add a delivery address to continue.")
        return redirect('add_address')

    if request.method == "POST":

        # Check stock before creating order
        for item in cart_items:
            if item.quantity > item.book.stock:
                messages.error(
                    request,
                    f"Only {item.book.stock} copy/copies of {item.book.title} available."
                )
                return redirect('view_cart')

        # Create pending order
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=total,
            status='pending'
        )

        # Create order items
        # IMPORTANT: stock is NOT reduced here
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.price
            )

        # Create Razorpay order
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        amount_in_paise = int(total * 100)

        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": 1
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        return render(request, "book_app/payment.html", {
            "order": order,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
            "amount": amount_in_paise,
        })

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
    
    # update status
    order.status = 'cancelled'  
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
    items = Wishlist.objects.filter(user=request.user).order_by('-added_at')  # get wishlist items
    return render(request, 'book_app/wishlist.html', {'items': items})


@login_required
def add_to_wishlist(request, book_id):
    Wishlist.objects.get_or_create(
        user=request.user,
        book=get_object_or_404(Book, id=book_id)
    )  # add book to wishlist
    
    messages.success(request, "Book added to wishlist.")
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, book_id):
    Wishlist.objects.filter(
        user=request.user,
        book_id=book_id
    ).delete()  # remove from wishlist

    messages.success(request, "Book removed from wishlist.")
    return redirect('wishlist')



# 12.PROFILE
# =========================
@login_required
def my_profile(request):
    profile = request.user.userprofile  # get profile linked to current user
    return render(request, 'book_app/my_profile.html', {
        'user': request.user,
        'profile': profile
    })



# 13.ADDRESS
# =========================
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)  # user's addresses-list
    return render(request, 'book_app/address_list.html', {'addresses': addresses})


@login_required
def select_address(request, address_id):
    # get selected address of current user
    address = get_object_or_404(Address, id=address_id, user=request.user)

    # save selected address in session
    request.session['selected_address_id'] = address.id

    messages.success(request, "Address selected successfully.")
    return redirect('checkout')  # go back to checkout


@login_required
def add_address(request):
    # Get next page from URL first, or from hidden input after form submit
    next_page = request.GET.get('next') or request.POST.get('next')

    form = AddressForm(request.POST or None)  # address form

    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)   # create address object first
        address.user = request.user         # connect address to logged-in user
        address.save()                      # save address in database

        # Make this new address the current selected address for checkout
        request.session['selected_address_id'] = address.id

        # If user came from checkout flow, go back to checkout
        if next_page == 'checkout':
            messages.success(request, "Address added successfully. Continue to checkout.")
            return redirect('checkout')

        # Normal address/profile flow
        messages.success(request, "Address added successfully.")
        return redirect('address_list')

    # Reuse add_address.html for add mode
    return render(request, 'book_app/add_address.html', {
        'form': form,
        'mode': 'add',
        'next': next_page,   # send next value to template
    })

#edit-address
@login_required
def edit_address(request, id):

    address = Address.objects.get(id=id, user=request.user)

    form = AddressForm(request.POST or None, instance=address)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(request, "Address updated successfully.")
        return redirect('address_list')
    # use add_address.html template to edit existing address
    return render(request, 'book_app/add_address.html', {'form': form, 'mode': 'edit'})
#reuse-add_address.html for editing.

#dlt-address
@login_required
def delete_address(request, id):

    address = Address.objects.get(id=id, user=request.user)
    address.delete()

    messages.success(request, "Address deleted successfully.")
    return redirect('address_list')


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


def test_razorpay(request):
    try:
        # Create Razorpay client (connect using the keys)
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Create a test order in Razorpay
        order = client.order.create({
            "amount": 50000,        # amount in paise - 500
            "currency": "INR",      # Indian currency
            "payment_capture": 1    # auto capture payment
        })

        # If success - show order ID in browser
        return HttpResponse(f"Success! Razorpay Order ID: {order['id']}")

    except Exception as e:
        # If error - show error message
        return HttpResponse(f"Error: {str(e)}")
    


@csrf_exempt
@login_required
def verify_payment(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    razorpay_payment_id = request.POST.get("razorpay_payment_id") or request.GET.get("razorpay_payment_id")
    razorpay_order_id = request.POST.get("razorpay_order_id") or request.GET.get("razorpay_order_id")
    razorpay_signature = request.POST.get("razorpay_signature") or request.GET.get("razorpay_signature")

    if not razorpay_payment_id:
        messages.error(request, "Payment failed or cancelled.")
        return redirect("checkout")

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    params_dict = {
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_signature": razorpay_signature,
    }

    try:
        client.utility.verify_payment_signature(params_dict)

        # Save payment details
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.status = "paid"
        order.save()

        # Reduce stock ONLY after successful payment
        for item in order.items.all():
            if item.quantity <= item.book.stock:
                item.book.stock -= item.quantity
                item.book.save()
            else:
                messages.error(request, f"Stock issue for {item.book.title}.")
                return redirect("checkout")

        # Clear cart
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()

        messages.success(request, "Payment successful!")
        return redirect("order_success")

    except Exception as e:
        print("SIGNATURE ERROR:", e)
        messages.error(request, "Payment verification failed.")
        return redirect("checkout")