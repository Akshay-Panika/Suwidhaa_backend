from django.db import models
from cloudinary.models import CloudinaryField

class College(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact number of the college"
    )
    category = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User can enter any category (e.g., Engineering, Medical, Arts, etc.)"
    )
    logo = CloudinaryField(
        'logo',
        folder='suwidhaa/college/logos',
        blank=True,
        null=True,
        help_text="College logo image"
    )
    is_recommended = models.BooleanField(
        default=False,
        help_text="Mark college as recommended (manual)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category or 'No Category'})"


class CollegeImage(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = CloudinaryField(
        'image',
        folder='suwidhaa/college/images',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.college.name}"