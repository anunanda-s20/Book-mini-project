from django.urls import path
from . import views

from django.conf import settings          # access MEDIA settings
from django.conf.urls.static import static # serve media files in development


urlpatterns = [

    # =========================
    # HOME & PUBLIC PAGES
    # =========================
    path('', views.home, name='home'),   # home page

    path('books/', views.book_list, name='book_list'),          # show all books
    path('books/<int:id>/', views.book_detail, name='book_detail'),  # single book detail


    # =========================
    # CART
    # =========================
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),  # add book to cart
    path('cart/', views.view_cart, name='view_cart'),                           # view cart
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),  # +
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),  # −


    # =========================
    # AUTHENTICATION
    # =========================
    path('signup/', views.signup, name='signup'),        # user signup
    path('login/', views.custom_login, name='login'),    # user login
    path('logout/', views.custom_logout, name='logout'), # user logout


    # =========================
    # BOOK MANAGEMENT (STAFF)
    # =========================
    path('add-book/', views.add_book, name='add_book'),  # add book (staff only)


    # =========================
    # DASHBOARD (STAFF)
    # =========================
    path('dashboard/', views.dashboard, name='dashboard'),  # admin dashboard
    path('dashboard/books/', views.manage_books, name='manage_books'),  # manage books
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),  # edit book
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),  # delete book


    # =========================
    # ORDERS (STAFF ACTION)
    # =========================
    path(
        'dashboard/orders/update/<int:order_id>/',
        views.update_order_status,
        name='update_order_status'
    ),  # staff updates order status


    # =========================
    # CHECKOUT & USER ORDERS
    # =========================
    path('checkout/', views.checkout, name='checkout'),          # checkout page
    path('order-success/', views.order_success, name='order_success'),  # order success page

    path('my-orders/', views.my_orders, name='my_orders'),  
    # ✅ USER orders page (THIS FIXES STATUS VISIBILITY)


    # =========================
    # WISHLIST
    # =========================
    path('wishlist/', views.wishlist, name='wishlist'),  # view wishlist
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # add
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # remove
]


# =========================
# MEDIA FILES (DEV ONLY)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
