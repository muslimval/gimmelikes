from django.db import models

# Create your models here.
# payments/models.py

from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('orange', 'Orange Money'),
        ('afrimoney', 'Afrimoney'),
        ('crypto', 'Cryptocurrency'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    points_purchased = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class PointPackage(models.Model):
    points = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.points} points for ${self.price}"