from django.db import models
from cloudinary.models import CloudinaryField


class EcommerceBanner(models.Model):
    banner_image = CloudinaryField(
        "banner_image",
        folder="suwidhaa/ecommerce/banner",
        blank=False,
        null=False,
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_banner"
        ordering = ["-id"]

    def __str__(self):
        return f"Ecommerce Banner {self.id} - {self.title or 'Untitled'}"