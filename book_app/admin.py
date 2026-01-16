from django.contrib import admin

# Register your models here.
from .models import Book, Order, BookImage, Cart, CartItem,OrderItem,Wishlist,Address


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'author')
    list_filter = ('published_date',)
    ordering = ('-published_date',)




admin.site.register(BookImage)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)