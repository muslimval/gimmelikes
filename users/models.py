from django.db import models

# users/models.py

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')
    facebook_connected = models.BooleanField(default=False)
    twitter_connected = models.BooleanField(default=False)
    instagram_connected = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} Profile'
