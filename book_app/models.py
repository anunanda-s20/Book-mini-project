from django.db import models#tools-db tables
from django.contrib.auth.models import User#django-built-in User model=auth
from django.db.models.signals import post_save#signal-run=model instance=saved
from django.dispatch import receiver#decorator=connect-funtion-to-signal


# 1.USER PROFILE ==========
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)#1-1=one user one profile,on dlt both removed
    phone = models.CharField(max_length=10, blank=True)#phone-optional field

    def __str__(self):
        return self.user.username#admin-display=username


@receiver(post_save, sender=User)#signal-trigger=after user saved
def create_user_profile(sender, instance, created, **kwargs):#checks-if-new user created
    if created:
        UserProfile.objects.create(user=instance)#auto-create profile for new user


@receiver(post_save, sender=User)#signal-trigger=after user saved
def save_user_profile(sender, instance, **kwargs):#checks-if-user updated
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()#auto-save related profile


# 2.CATEGORY ==========
class Category(models.Model):
    title = models.CharField(max_length=100)#category-name
    description = models.TextField(blank=True)#category-description optional
    image = models.ImageField(
        upload_to='category_images/',
        blank=True,
        default='category_images/default.png'
    )#category-image path/default image

    def __str__(self):
        return self.title#return-category-title


# 3.BOOK ==========
class Book(models.Model):

    # separate books vs accessories
    PRODUCT_TYPE_CHOICES = (
        ('book', 'Book'),
        ('accessory', 'Accessory'),
    )#choices=restrict values

    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default='book'
    )#store-product-type with choices

    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)#1-many=category-books,set null if category deleted

    title = models.CharField(max_length=200)#book-title

    author = models.CharField(
        max_length=100,
        blank=True
    )#author optional (for accessories)

    price = models.DecimalField(max_digits=8, decimal_places=2)#price-decimal value
    description = models.TextField(blank=True)#book-description optional

    stock = models.PositiveIntegerField(default=0)#stock>=0 only
    is_active = models.BooleanField(default=True)#show/hide product

    published_date = models.DateField(null=True, blank=True)#publish-date optional

    created_at = models.DateTimeField(auto_now_add=True)#auto-store-created datetime
    updated_at = models.DateTimeField(auto_now=True)#auto-update datetime

    def __str__(self):
        return self.title#return-book-title3

    @property#dynamic-calculated field
    def availability_status(self):#returns-stock status
        return "In Stock" if self.stock > 0 else "Out of Stock"#check-stock


# 4.BOOK IMAGE ==========
class BookImage(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE,related_name='images')#1-many=one book many images,on dlt remove images
    image = models.ImageField(upload_to='book_images/')#store-image-path

    def __str__(self):
        return f"Image for {self.book.title}"#display-image-of-book


# 5.ADDRESS ==========
class Address(models.Model):#store-user-address
    user = models.ForeignKey(User, on_delete=models.CASCADE)#1-many=one user many addresses
    full_name = models.CharField(max_length=100)#receiver-name
    phone = models.CharField(max_length=15)#contact-number
    street = models.CharField(max_length=255)#street-address
    city = models.CharField(max_length=50)#city-name
    state = models.CharField(max_length=50)#state-name
    pincode = models.CharField(max_length=10)#postal-code
    created_at = models.DateTimeField(auto_now_add=True)#created datetime

    def __str__(self):
        return f"{self.full_name} - {self.city}"#display-name-city


#  6.ORDER =================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]#order-status options

    user = models.ForeignKey(User, on_delete=models.CASCADE)#1-many=one user many orders
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)#order-linked-address,set null if deleted
    total_price = models.DecimalField(max_digits=8, decimal_places=2)#total-order-price
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')#current-order-status
    created_at = models.DateTimeField(auto_now_add=True)#order-created datetime
    updated_at = models.DateTimeField(auto_now=True)#order-updated datetime

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"#display-order-id-user

#8.OrderItem
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')#1-many=one order many items
    book = models.ForeignKey(Book, on_delete=models.CASCADE)#order-related-book
    quantity = models.PositiveIntegerField(default=1)#book-quantity
    price = models.DecimalField(max_digits=8, decimal_places=2)#book-price-at-time-of-order

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"#display-book-quantity


#  9.CART =================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)#1-1=one user one cart
    created_at = models.DateTimeField(auto_now_add=True)#cart-creation time

    def __str__(self):
        return f"Cart of {self.user.username}"#display-cart-owner

# 10.CartItems
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')#1-many=one cart many items
    book = models.ForeignKey(Book, on_delete=models.CASCADE)#cart-related-book
    quantity = models.PositiveIntegerField(default=1)#book-quantity-in-cart

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"#display-cart-item


# 11. WISHLIST =================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)#1-many=one user many wishlist-items
    book = models.ForeignKey(Book, on_delete=models.CASCADE)#1-many=one book many wishlist-entries
    added_at = models.DateTimeField(auto_now_add=True)#wishlist-added datetime

    class Meta:
        unique_together = ('user', 'book')#prevent-duplicate user-book pair

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"#display-user-book
