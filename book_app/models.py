from django.db import models  # Django models
from django.contrib.auth.models import User  # default user


class Book(models.Model):
    title = models.CharField(max_length=200)  # book title
    author = models.CharField(max_length=100)  # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # book price
    published_date = models.DateField()  # publish date

    def __str__(self): return self.title  # show title


class BookImage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')  # link to book
    image = models.ImageField(upload_to='book_images/')  # book image

    def __str__(self): return f"Image for {self.book.title}"  # show book name


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
