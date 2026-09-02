from django.db import models
from cloudinary.models import CloudinaryField


class CollegeBanner(models.Model):
    banner_image = CloudinaryField(
        "banner_image",
        folder="suwidhaa/college/banner",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"College Banner {self.id}"