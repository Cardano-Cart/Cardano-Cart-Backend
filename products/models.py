from django.db import models
from django.conf import settings
from django.utils import timezone

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # References the seller from the User model
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Use Decimal for better handling of money
    stock = models.IntegerField()
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, null=True)
    sku = models.CharField(max_length=100, unique=True, null=True)
    specifications = models.JSONField(null=True)  # Store specifications as JSON
    images = models.ManyToManyField('ProductImage', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')
