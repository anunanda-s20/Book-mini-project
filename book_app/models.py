from django.db import models
from django.contrib.auth.models import User


# Book model (NO change needed)
class Book(models.Model):
    title = models.CharField(max_length=200)          # book name
    author = models.CharField(max_length=100)         # author name
    price = models.DecimalField(max_digits=6, decimal_places=2)  # book price
    published_date = models.DateField()               # publish date

    def __str__(self):
        return self.title


# Order model (UPDATED with status)
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),       # order created, not paid yet
        ('paid', 'Paid'),             # payment completed
        ('shipped', 'Shipped'),       # order sent to customer
        ('delivered', 'Delivered'),   # order successfully delivered
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )  # which user placed the order

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )  # which book was ordered

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )  # price at the time of order

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )  # current order status

    ordered_at = models.DateTimeField(
        auto_now_add=True
    )  # date & time of order

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.status}"
