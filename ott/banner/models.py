from django.db import models
from cloudinary.models import CloudinaryField


class Banner(models.Model):
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ott/banners",
        blank=False,
        null=False,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Banner #{self.pk}"