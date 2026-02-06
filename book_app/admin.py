from django.contrib import admin
from .models import (
    UserProfile,
    Book,
    BookImage,
    Address,
    Order,
    OrderItem,
    Cart,
    CartItem,
    Wishlist,
    Category
)

# ================= USER PROFILE =================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


# ================= BOOK =================
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'stock', 'is_active', 'category')
    list_filter = ('is_active', 'category')
    search_fields = ('title', 'author')
    ordering = ('title',)


# ================= BOOK IMAGE =================
@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ('book',)


# ================= CATEGORY =================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')  # fixed to use 'title' from model
    search_fields = ('title',)


# ================= ADDRESS =================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'city', 'state', 'pincode')
    search_fields = ('full_name', 'city', 'pincode')
    list_filter = ('city', 'state')


# ================= ORDER ITEM INLINE =================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('book', 'quantity', 'price')
    extra = 0
    can_delete = False


# ================= ORDER =================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    ordering = ('-created_at',)
    readonly_fields = ('user', 'total_price', 'created_at', 'address')
    inlines = [OrderItemInline]


# ================= CART =================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'book', 'quantity')


# ================= WISHLIST =================
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')
