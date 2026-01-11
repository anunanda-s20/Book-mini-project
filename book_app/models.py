from django.db import models  # Django models
from django.contrib.auth.models import User  # default user

#BOOK MODEL
class Book(models.Model):
    title = models.CharField(max_length=200)  # book title
    author = models.CharField(max_length=100)  # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # book price
    published_date = models.DateField()  # publish date

    def __str__(self): return self.title  # show title

#BOOK-IMG MODEL
class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')  # link to book
    image = models.ImageField(upload_to='book_images/')  # book image

    def __str__(self): return f"Image for {self.book.title}"  # show book name

#ORDER MODEL
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),      # order created
        ('paid', 'Paid'),            # payment done
        ('shipped', 'Shipped'),      # order shipped
        ('delivered', 'Delivered'),  # order delivered
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # order user
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ordered book
    price = models.DecimalField(max_digits=8, decimal_places=2)  # order price
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # order status
    ordered_at = models.DateTimeField(auto_now_add=True)  # order time

    def __str__(self): return f"{self.user.username} - {self.book.title} - {self.status}"  # readable text



# CART MODELS
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # cart owner
    created_at = models.DateTimeField(auto_now_add=True)  # cart created time

    def __str__(self): return f"Cart of {self.user.username}"  # readable text


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')  # linked cart
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # book in cart
    quantity = models.PositiveIntegerField(default=1)  # book quantity

    def __str__(self): return f"{self.book.title} x {self.quantity}"  # readable text
