from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import Book, Order
from .forms import SimpleUserCreationForm, BookForm


# =========================
# PUBLIC PAGES
# =========================

def home(request):
    return render(request, 'book_app/home.html')


@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_app/book_list.html', {'books': books})


@login_required
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})


# =========================
# AUTHENTICATION
# =========================

def signup(request):
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


def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html')


@login_required
def custom_logout(request):
    logout(request)
    return redirect('home')


# =========================
# BOOK CRUD (STAFF)
# =========================

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

def staff_required(user):
    return user.is_staff


@login_required
@user_passes_test(staff_required)
def dashboard(request):
    books = Book.objects.all()
    orders = Order.objects.all().order_by('-ordered_at')

    context = {
        'books': books,
        'orders': orders,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@user_passes_test(staff_required)
def manage_books(request):
    books = Book.objects.all()
    return render(request, 'dashboard/manage_books.html', {'books': books})


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


@login_required
@user_passes_test(staff_required)
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('manage_books')


# =========================
# ORDER STATUS UPDATE
# =========================

@login_required
@user_passes_test(staff_required)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()

    return redirect('dashboard')


# =========================
# PAYMENT (SIMULATION)
# =========================

@login_required
def buy_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    Order.objects.create(
        user=request.user,
        book=book,
        price=book.price
    )

    return redirect('payment_success')


@login_required
def payment_success(request):
    return render(request, 'book_app/payment_success.html')
