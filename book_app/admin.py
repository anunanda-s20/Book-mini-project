from django.contrib import admin

# Register your models here.
from .models import Book, Order


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date')
    search_fields = ('title', 'author')
    list_filter = ('published_date',)
    ordering = ('-published_date',)



admin.site.register(Order)