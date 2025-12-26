from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Book
from .forms import SimpleUserCreationForm


# HOME PAGE
# This page is visible to everyone (logged in or not)
def home(request):
    return render(request, 'book_app/home.html')


# BOOK LIST PAGE (login required)
# Only logged-in users can see the list of books
@login_required
def book_list(request):
    books = Book.objects.all()  # get all books from database
    return render(request, 'book_app/book_list.html', {'books': books})


# BOOK DETAIL PAGE (login required)
# Shows details of one book using its ID
@login_required
def book_detail(request, id):
    book = get_object_or_404(Book, id=id)  # get book or show 404 error
    return render(request, 'book_app/book_detail.html', {'book': book})


# SIGNUP PAGE
# Logged-in users should NOT access signup page
def signup(request):
    # 🔒 If user is already logged in → send to home
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = SimpleUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Django built-in login page
    else:
        form = SimpleUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})
