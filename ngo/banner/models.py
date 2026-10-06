from django.db import models
from cloudinary.models import CloudinaryField


class NgoBanner(models.Model):
    banner_image = CloudinaryField(
        "banner_image",
        folder="suwidhaa/ngo/banner",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"NGO Banner {self.id}"