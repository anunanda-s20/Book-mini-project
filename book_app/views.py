from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Book, Order
from .forms import SimpleUserCreationForm, BookForm



# HOME PAGE
# Visible to everyone
def home(request):
    return render(request, 'book_app/home.html')


# BOOK LIST PAGE (READ)
# Login required
@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_app/book_list.html', {'books': books})


# BOOK DETAIL PAGE (READ)
# Login required
@login_required
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})


# SIGNUP PAGE
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


# ADD BOOK (CREATE)
# Login required
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


# DASHBOARD (STAFF ONLY)

# Staff check
def staff_required(user):
    return user.is_staff


# DASHBOARD HOME
@login_required
@user_passes_test(staff_required)
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


# MANAGE BOOKS (READ)
@login_required
@user_passes_test(staff_required)
def manage_books(request):
    books = Book.objects.all()
    return render(request, 'dashboard/manage_books.html', {'books': books})


# EDIT BOOK (UPDATE)
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
@login_required
@user_passes_test(staff_required)
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('manage_books')



# BUY BOOK (PAYMENT - SIMULATION)
# Login required
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
@login_required
def payment_success(request):
    return render(request, 'book_app/payment_success.html')
