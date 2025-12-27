from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # home page
    path('books/', views.book_list, name='book_list'),
    path('books/<int:id>/', views.book_detail, name='book_detail'),#book detail pg
    path('signup/', views.signup, name='signup'),
    path('add-book/', views.add_book, name='add_book'),
]