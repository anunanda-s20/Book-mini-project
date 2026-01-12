from django.db import models  # Django models
from django.contrib.auth.models import User  # default user

# -----------------------------
# BOOK MODEL
# -----------------------------
class Book(models.Model):
    title = models.CharField(max_length=200)  # book title
    author = models.CharField(max_length=100)  # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # book price
    published_date = models.DateField()  # publish date

    def __str__(self):
        return self.title  # show title


# -----------------------------
# BOOK IMAGE MODEL
# -----------------------------
class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')  # link to book
    image = models.ImageField(upload_to='book_images/')  # book image

    def __str__(self):
        return f"Image for {self.book.title}"


# -----------------------------
# ORDER MODELS
# -----------------------------

# Order = one order by one user
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),      # order created
        ('paid', 'Paid'),            # payment done
        ('shipped', 'Shipped'),      # order shipped
        ('delivered', 'Delivered'),  # order delivered
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # who ordered
    total_price = models.DecimalField(max_digits=8, decimal_places=2)  # total price of order
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # order status
    ordered_at = models.DateTimeField(auto_now_add=True)  # time of order

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} - {self.status}"


# OrderItem = each book inside one order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')  # linked order
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # book in order
    quantity = models.PositiveIntegerField(default=1)  # quantity of book
    price = models.DecimalField(max_digits=8, decimal_places=2)  # price of book (for record)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


# -----------------------------
# CART MODELS
# -----------------------------
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # cart owner
    created_at = models.DateTimeField(auto_now_add=True)  # cart created time

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # linked cart
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # book in cart
    quantity = models.PositiveIntegerField(default=1)  # book quantity

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"
