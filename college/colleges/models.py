from django.db import models
from cloudinary.models import CloudinaryField

class College(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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
        null=True  # Allow null for testing
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.college.name}"