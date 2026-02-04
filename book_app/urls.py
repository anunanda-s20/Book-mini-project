from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # =========================
    # HOME & PUBLIC PAGES
    # =========================
    path('', views.home, name='home'),  # Home page
    path('books/', views.book_list, name='book_list'),  # List all books
    path('books/<int:id>/', views.book_detail, name='book_detail'),  # Book detail

    # =========================
    # CART SYSTEM
    # =========================
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),  # Add book to cart
    path('cart/', views.view_cart, name='view_cart'),  # View cart
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),  # Increase qty
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),  # Decrease qty
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Remove item

    # =========================
    # AUTHENTICATION
    # =========================
    path('signup/', views.signup, name='signup'),  # User signup
    path('login/', views.custom_login, name='login'),  # User login
    path('logout/', views.custom_logout, name='logout'),  # Logout

    # =========================
    # USER PROFILE & ADDRESSES
    # =========================
    path('profile/', views.my_profile, name='my_profile'),  # My profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # Edit profile
    path('addresses/', views.address_list, name='address_list'),  # List all addresses
    path('addresses/add/', views.add_address, name='add_address'),  # Add address
    # =========================
    # STAFF BOOK MANAGEMENT
    # =========================
    path('add-book/', views.add_book, name='add_book'),  # Add book (staff)
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard
    path('dashboard/books/', views.manage_books, name='manage_books'),  # Manage books
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),  # Edit book
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),  # Delete book

    # =========================
    # ORDERS (STAFF)
    # =========================
    path('dashboard/order/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),  # Order detail + update status

    # =========================
    # CHECKOUT & USER ORDERS
    # =========================
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('order-success/', views.order_success, name='order_success'),  # Order success
    path('my-orders/', views.my_orders, name='my_orders'),  # User's orders
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),  # Cancel order

    # =========================
    # WISHLIST
    # =========================
    path('wishlist/', views.wishlist, name='wishlist'),  # Wishlist page
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # Add to wishlist
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # Remove from wishlist
]

# =========================
# MEDIA FILES (DEV MODE)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
