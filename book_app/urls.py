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
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # =========================
    # AUTHENTICATION
    # =========================
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # =========================
    # USER PROFILE & ADDRESSES
    # =========================
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    #Address-edit & dlt
    path('address/edit/<int:id>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:id>/', views.delete_address, name='delete_address'),
    #Address-select
    path('select-address/<int:address_id>/', views.select_address, name='select_address'),

    # =========================
    # STAFF BOOK MANAGEMENT
    # =========================
    path('add-book/', views.add_book, name='add_book'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/books/', views.manage_books, name='manage_books'),
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),

    # =========================
    # ORDERS (STAFF)
    # =========================
    path('dashboard/order/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),

    # =========================
    # CHECKOUT & USER ORDERS
    # =========================
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # =========================
    # WISHLIST
    # =========================
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # =========================
    # ABOUT PAGE
    # =========================
    path('about/', views.about, name='about'),  #  Moved inside urlpatterns
    #categories-home-page
    path('category/<int:category_id>/', views.category_books, name='category_books'),

    # =========================
    # PAYMENT
    # =========================
    path("test-razorpay/", views.test_razorpay, name="test_razorpay"),
    path("verify-payment/<int:order_id>/", views.verify_payment, name="verify_payment"),
]



# =========================
# MEDIA FILES (DEV MODE)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
