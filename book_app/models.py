from django.db import models
from django.contrib.auth.models import User


# =============================
# BOOK MODEL
# =============================
class Book(models.Model):
    title = models.CharField(max_length=200)          # book name
    author = models.CharField(max_length=100)         # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # price
    published_date = models.DateField()               # publish date

    def __str__(self):
        return self.title


# =============================
# BOOK IMAGE MODEL
# =============================
class BookImage(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='images'
    )                                                  # image belongs to book
    image = models.ImageField(upload_to='book_images/')  # image file

    def __str__(self):
        return f"Image for {self.book.title}"


# =============================
# ORDER MODELS
# =============================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),        # order created
        ('paid', 'Paid'),              # payment done
        ('shipped', 'Shipped'),        # shipped
        ('delivered', 'Delivered'),    # delivered
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # order owner
    total_price = models.DecimalField(max_digits=8, decimal_places=2)  # final amount
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )                                                         # order status
    ordered_at = models.DateTimeField(auto_now_add=True)     # order time

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )                                    # item belongs to order
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ordered book
    quantity = models.PositiveIntegerField(default=1)         # quantity
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price at order time

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# =============================
# CART MODELS
# =============================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # one cart per user
    created_at = models.DateTimeField(auto_now_add=True)         # created time

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )                                     # item belongs to cart
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # cart book
    quantity = models.PositiveIntegerField(default=1)         # quantity

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# =============================
# WISHLIST MODEL
# =============================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # wishlist owner
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # wished book
    added_at = models.DateTimeField(auto_now_add=True)        # added time

    class Meta:
        unique_together = ('user', 'book')  
        # prevents same book being added twice by same user

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
