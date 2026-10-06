from django.db import models
from cloudinary.models import CloudinaryField


class NgoCategory(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,   # 👈 DB-level duplicate prevention
    )
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ngo/category",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"NGO Category {self.id} - {self.name}"