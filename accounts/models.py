from django.db import models
from django.contrib.auth.models import AbstractUser


from .managers import CustomUserManager



class CustomUser(AbstractUser):
    phone = models.CharField(max_length=11, unique=True)
    username = models.CharField(max_length=50, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []


class OtpCode(models.Model):
    phone = models.CharField(max_length=11, unique=True)
    code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.code)
    
