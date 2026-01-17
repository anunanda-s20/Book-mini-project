from django.contrib import admin  # admin tools
from .models import Book, BookImage, Order, OrderItem, Wishlist, Address, Cart, CartItem  # import models

# ---------------- Book admin ----------------
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'stock', 'is_active')  # show main book info
    list_filter = ('is_active',)  # filter active/inactive books
    search_fields = ('title', 'author')  # search by title/author
    ordering = ('title',)  # alphabetical order

# ---------------- OrderItems inline ----------------
class OrderItemInline(admin.TabularInline):  
    model = OrderItem  # connect OrderItems to Orders
    readonly_fields = ('book', 'quantity', 'price')  # prevent editing
    extra = 0  # no empty rows
    can_delete = False  # prevent deletion from admin

# ---------------- Order admin ----------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'ordered_at')  # Order ID + summary
    list_filter = ('status',)  # filter by order status
    ordering = ('-ordered_at',)  # newest orders first
    inlines = [OrderItemInline]  # show items inside order
    readonly_fields = ('user', 'total_price', 'ordered_at', 'address')  # protect core data

# ---------------- Other models ----------------
admin.site.register(BookImage)  # manage book images
admin.site.register(Address)    # view addresses
admin.site.register(Wishlist)   # view wishlists
admin.site.register(Cart)       # view carts
admin.site.register(CartItem)   # view cart items
