from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # home page
    path('books/', views.book_list, name='book_list'),
    path('books/<int:id>/', views.book_detail, name='book_detail'),#book detail pg
    path('signup/', views.signup, name='signup'),
    path('add-book/', views.add_book, name='add_book'),
    #dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/books/', views.manage_books, name='manage_books'),
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),

]