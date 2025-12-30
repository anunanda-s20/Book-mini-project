from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .models import Book, Order
from .forms import SimpleUserCreationForm, BookForm
from django.contrib.auth import logout

# HOME PAGE
# Visible to everyone
def home(request):
    return render(request, 'book_app/home.html')


# BOOK LIST PAGE (READ)
# Login required (admin OR normal user)
@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_app/book_list.html', {'books': books})


# BOOK DETAIL PAGE (READ)
# Login required (admin OR normal user)
@login_required
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})


# SIGNUP PAGE
# Only for NOT logged-in users
def signup(request):
    # If already logged in → redirect to home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SimpleUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})


# LOGIN PAGE
# Only for NOT logged-in users
def custom_login(request):
    # If already logged in → redirect to home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # or 'dashboard' if staff
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


# CUSTOM LOGOUT
@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')  # redirect to home page after logout


# ADD BOOK (CREATE)
# Login required (admin OR normal user)
@login_required
def add_book(request):
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

# Staff check
def staff_required(user):
    return user.is_staff


# DASHBOARD HOME
# Only staff users allowed
@login_required
@user_passes_test(staff_required)
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


# MANAGE BOOKS (READ)
# Only staff users allowed
@login_required
@user_passes_test(staff_required)
def manage_books(request):
    books = Book.objects.all()
    return render(request, 'dashboard/manage_books.html', {'books': books})


# EDIT BOOK (UPDATE)
# Only staff users allowed
@login_required
@user_passes_test(staff_required)
def edit_book(request, id):
    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('manage_books')
    else:
        form = BookForm(instance=book)

    return render(request, 'dashboard/edit_book.html', {'form': form})


# DELETE BOOK (DELETE)
# Only staff users allowed
@login_required
@user_passes_test(staff_required)
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('manage_books')


# PAYMENT (SIMULATION)


# BUY BOOK (PAYMENT - SIMULATION)
# Login required (normal users)
@login_required
def buy_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    # Fake payment success (save order)
    Order.objects.create(
        user=request.user,
        book=book,
        price=book.price
    )

    return redirect('payment_success')


# PAYMENT SUCCESS PAGE
# Login required
@login_required
def payment_success(request):
    return render(request, 'book_app/payment_success.html')
