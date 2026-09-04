from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
import random
import string

class User(AbstractUser):
    # Custom User model with additional fields
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    profile_image = CloudinaryField(
        "profile_image", 
        folder="suwidhaa/user",
        blank=True, 
        null=True
    )
    email = models.EmailField(max_length=254, null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    
    # Add related_name to avoid conflicts with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='app_auth_user_groups',  # Changed from user_set
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='app_auth_user_permissions',  # Changed from user_set
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )
    
    # Remove username requirement and use phone as unique identifier
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['username']  # Django requires username field
    
    class Meta:
        db_table = 'app_auth_user'  # Optional: explicit table name
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} - {self.phone}"

class OTP(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='otps'
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return ''.join(random.choices(string.digits, k=6))
    
    class Meta:
        db_table = 'app_auth_otp'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.phone} - {self.otp_code}"