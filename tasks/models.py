from django.db import models

# Create your models here.
# tasks/models.py

from django.db import models
from django.contrib.auth.models import User

class SocialTask(models.Model):
    TASK_TYPES = (
        ('like', 'Like'),
        ('follow', 'Follow'),
        ('share', 'Share'),
        ('subscribe', 'Subscribe'),
    )
    
    PLATFORMS = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
    )
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=10, choices=TASK_TYPES)
    platform = models.CharField(max_length=10, choices=PLATFORMS)
    points_reward = models.IntegerField()
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(SocialTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
