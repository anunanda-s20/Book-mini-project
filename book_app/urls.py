from django.urls import path
from . import views

from django.conf import settings          # access MEDIA settings
from django.conf.urls.static import static # serve media files in development

urlpatterns = [
    path('', views.home, name='home'),   # home page

    path('books/', views.book_list, name='book_list'),  # all books
    path('books/<int:id>/', views.book_detail, name='book_detail'),  # book detail

    # -----------------
    # CART
    # -----------------
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),  # add book to cart
    path('cart/', views.view_cart, name='view_cart'),                           # view cart
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),  # +
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),  # −

    # -----------------
    # AUTH
    # -----------------
    path('signup/', views.signup, name='signup'),        # signup page
    path('login/', views.custom_login, name='login'),    # custom login
    path('logout/', views.custom_logout, name='logout'), # logout

    # -----------------
    # BOOK MANAGEMENT
    # -----------------
    path('add-book/', views.add_book, name='add_book'),  # add book

    # -----------------
    # DASHBOARD
    # -----------------
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/books/', views.manage_books, name='manage_books'),
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),

    # -----------------
    # PAYMENT & ORDERS
    # -----------------
    #path('buy/<int:book_id>/', views.buy_book, name='buy_book'),
    #path('payment-success/', views.payment_success, name='payment_success'),
    path('dashboard/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),

    # -----------------
    # CHECKOUT
    # -----------------
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),

    # -----------------
    # WISHLIST
    # -----------------
    path('wishlist/', views.wishlist, name='wishlist'),  # view wishlist
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # add to wishlist
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # remove from wishlist
]

# Serve uploaded images (MEDIA) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
