from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
import os
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    gender = models.CharField(max_length=50)
    is_login = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

class chatMessages(models.Model):
    user_from = models.ForeignKey(User,
        on_delete=models.CASCADE,related_name="+")
    user_to = models.ForeignKey(User,
        on_delete=models.CASCADE,related_name="+")
    message = models.TextField()
    image = models.ImageField(upload_to=os.path.join('images/'), blank=True, null=True)
    pdf_file = models.FileField(upload_to='images/doc/pdf', blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    can_forward = models.BooleanField(default=True)
    forwarding_enabled = models.BooleanField(default=True)
     

    def __str__(self):
        return self.message
            
