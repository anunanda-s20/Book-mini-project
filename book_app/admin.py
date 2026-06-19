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
    Category,
)

# ================= USER PROFILE =================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


# ================= BOOK (MAIN) =================
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    # columns shown in admin list page (table view)
    list_display = ('title', 'product_type', 'author', 'price', 'stock', 'is_active', 'category')

    # filters on right side (filter by type, category, status)
    list_filter = ('product_type', 'category', 'is_active')

    # search bar (search by title or author)
    search_fields = ('title', 'author')

    # default ordering (alphabetical by title)
    ordering = ('title',)

    # fields shown in add/edit form (IMPORTANT FIX)
    # this makes "product_type" visible in admin form
    fields = (
        'product_type',   # choose Book or Accessory
        'title',          # product name
        'author',         # author name
        'price',          # price
        'stock',          # quantity available
        'is_active',      # show/hide product
        'category',       # category (UI purpose)
        'description',    # details
        'published_date'  # optional date
    )

# ================= BOOK IMAGE =================
@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ('book',)


# ================= CATEGORY =================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
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
