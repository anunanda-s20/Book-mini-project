from django.db import models
from django.contrib.auth.models import User


# ================= BOOK =================
class Book(models.Model):
    title = models.CharField(max_length=200)              # book title
    author = models.CharField(max_length=100)             # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # price
    description = models.TextField(blank=True)            # description
    stock = models.PositiveIntegerField(default=0)        # stock count
    is_active = models.BooleanField(default=True)         # active flag
    published_date = models.DateField(blank=True, null=True)  # publish date
    created_at = models.DateTimeField(auto_now_add=True)  # created time
    updated_at = models.DateTimeField(auto_now=True)      # updated time

    def __str__(self):
        return self.title


# ================= BOOK IMAGE =================
class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')  # linked book
    image = models.ImageField(upload_to='book_images/')  # image file

    def __str__(self):
        return f"Image for {self.book.title}"


# ================= ADDRESS =================
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # owner
    full_name = models.CharField(max_length=100)              # receiver name
    phone = models.CharField(max_length=15)                   # phone
    street = models.TextField()                               # street
    city = models.CharField(max_length=50)                    # city
    state = models.CharField(max_length=50)                   # state
    pincode = models.CharField(max_length=10)                 # pincode
    created_at = models.DateTimeField(auto_now_add=True)      # created time

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# ================= ORDER =================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # buyer
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)  # delivery address
    total_price = models.DecimalField(max_digits=8, decimal_places=2)  # order total
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # order status
    created_at = models.DateTimeField(auto_now_add=True)      # order time
    updated_at = models.DateTimeField(auto_now=True)          # update time

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


# ================= ORDER ITEM =================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # parent order
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # book
    quantity = models.PositiveIntegerField(default=1)         # quantity
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price snapshot

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# ================= CART =================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # cart owner
    created_at = models.DateTimeField(auto_now_add=True)         # created time

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # parent cart
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # book
    quantity = models.PositiveIntegerField(default=1)         # quantity

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# ================= WISHLIST =================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # book
    added_at = models.DateTimeField(auto_now_add=True)        # added time

    class Meta:
        unique_together = ('user', 'book')  # no duplicates

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
