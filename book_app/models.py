from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# =============================
# BOOK MODEL
# =============================
class Book(models.Model):
    title = models.CharField(max_length=200)           # book name
    author = models.CharField(max_length=100)          # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # price

    description = models.TextField(blank=True)         # optional description
    stock = models.PositiveIntegerField(default=0)     # available stock
    is_active = models.BooleanField(default=True)      # show/hide book
    published_date = models.DateField(blank=True, null=True)  # optional publish date

    created_at = models.DateTimeField(auto_now_add=True)  # book added time
    updated_at = models.DateTimeField(auto_now=True)      # last updated

    def __str__(self):
        return self.title


# =============================
# BOOK IMAGE MODEL
# =============================
class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')  # belongs to book
    image = models.ImageField(upload_to='book_images/')                               # image file

    def __str__(self):
        return f"Image for {self.book.title}"


# =============================
# ADDRESS MODEL
# =============================
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # address owner
    full_name = models.CharField(max_length=100)              # receiver name
    phone = models.CharField(max_length=15)                  # contact number
    street = models.TextField()                               # street / address
    city = models.CharField(max_length=50)                   # city
    state = models.CharField(max_length=50)                  # state
    pincode = models.CharField(max_length=10)                # postal code
    created_at = models.DateTimeField(auto_now_add=True)     # added time

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# =============================
# ORDER MODEL
# =============================
class Order(models.Model):
    # Updated status choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)                  # order owner
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)  # shipping address
    total_price = models.DecimalField(max_digits=8, decimal_places=2)         # final amount
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # order status
    ordered_at = models.DateTimeField(auto_now_add=True)                       # order created
    updated_at = models.DateTimeField(auto_now=True)                           # last update

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


# =============================
# ORDER ITEM MODEL
# =============================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # belongs to order
    book = models.ForeignKey(Book, on_delete=models.CASCADE)                           # ordered book
    quantity = models.PositiveIntegerField(default=1)                                  # quantity
    price = models.DecimalField(max_digits=8, decimal_places=2)                        # price at order time

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# =============================
# CART MODELS
# =============================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # one cart per user
    created_at = models.DateTimeField(auto_now_add=True)         # cart created

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # belongs to cart
    book = models.ForeignKey(Book, on_delete=models.CASCADE)                          # cart book
    quantity = models.PositiveIntegerField(default=1)                                  # quantity

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# =============================
# WISHLIST MODEL
# =============================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # owner
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # wished book
    added_at = models.DateTimeField(auto_now_add=True)        # added time

    class Meta:
        unique_together = ('user', 'book')  # prevent duplicates

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
