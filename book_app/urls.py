from django.urls import path
from . import views

from django.conf import settings           # media settings
from django.conf.urls.static import static # serve media files

urlpatterns = [

    # =========================
    # HOME & PUBLIC PAGES
    # =========================
    path('', views.home, name='home'),                       # home page
    path('books/', views.book_list, name='book_list'),       # all books
    path('books/<int:id>/', views.book_detail, name='book_detail'),  # book detail

    # =========================
    # CART
    # =========================
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),   # add to cart
    path('cart/', views.view_cart, name='view_cart'),                            # view cart
    path('cart/increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),  # +
    path('cart/decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),  # −
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),      # delete item ❌

    # =========================
    # AUTHENTICATION
    # =========================
    path('signup/', views.signup, name='signup'),          # signup
    path('login/', views.custom_login, name='login'),      # login
    path('logout/', views.custom_logout, name='logout'),   # logout

    # =========================
    # BOOK MANAGEMENT (STAFF)
    # =========================
    path('add-book/', views.add_book, name='add_book'),    # add book

    # =========================
    # DASHBOARD (STAFF)
    # =========================
    path('dashboard/', views.dashboard, name='dashboard'),  # dashboard
    path('dashboard/books/', views.manage_books, name='manage_books'),  # manage books
    path('dashboard/books/edit/<int:id>/', views.edit_book, name='edit_book'),  # edit book
    path('dashboard/books/delete/<int:id>/', views.delete_book, name='delete_book'),  # delete book

    # =========================
    # ORDERS (STAFF)
    # =========================
    path('dashboard/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),  # update order
    path('dashboard/order/<int:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),  # order detail

    # =========================
    # CHECKOUT & USER ORDERS
    # =========================
    path('checkout/', views.checkout, name='checkout'),              # checkout
    path('order-success/', views.order_success, name='order_success'),  # success page
    path('my-orders/', views.my_orders, name='my_orders'),           # user orders

    # =========================
    # WISHLIST
    # =========================
    path('wishlist/', views.wishlist, name='wishlist'),                      # view wishlist
    path('wishlist/add/<int:book_id>/', views.add_to_wishlist, name='add_to_wishlist'),  # add
    path('wishlist/remove/<int:book_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),  # remove
]

# =========================
# MEDIA FILES (DEV ONLY)
# =========================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
