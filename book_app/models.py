from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    published_date = models.DateField()

    def __str__(self):
        return self.title

from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)#which-user
    book = models.ForeignKey(Book, on_delete=models.CASCADE)#which-book
    price = models.DecimalField(max_digits=8, decimal_places=2)#price-taken book
    ordered_at = models.DateTimeField(auto_now_add=True)#date and time of order

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
