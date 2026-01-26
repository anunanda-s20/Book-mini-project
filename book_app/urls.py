from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # HOME & PUBLIC PAGES
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:id>/', views.book_detail, name='book_detail'),

    # CART
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # AUTHENTICATION
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # STAFF BOOK MANAGEMENT
    path('add-book/', views.add_book, name='add_book'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/books/', views.manage_books, name='manage_books'),
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),

    # ORDERS (STAFF)
    path('dashboard/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('dashboard/order/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),

    # CHECKOUT & USER ORDERS
    path('checkout/', views.checkout, name='checkout'),              # checkout page
    path('order-success/', views.order_success, name='order_success'),  # success page
    path('my-orders/', views.my_orders, name='my_orders'),

    # WISHLIST
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
