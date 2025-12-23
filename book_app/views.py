from django.shortcuts import render,get_object_or_404
from .models import Book

# Create your views here.
def home(request):
    return render(request, 'book_app/home.html')



def book_list(request):
    books = Book.objects.all()  # Get all books
    return render(request, 'book_app/book_list.html', {'books': books})

def book_detail(request, id):
    book = get_object_or_404(Book, id=id)
    return render(request, 'book_app/book_detail.html', {'book': book})