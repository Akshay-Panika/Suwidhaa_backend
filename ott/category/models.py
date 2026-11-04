from django.db import models
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
    )

    image = CloudinaryField(
        "image",
        folder="suwidhaa/ott/categories",
        blank=False,
        null=False,
    )

    # ❌ category_type removed

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name