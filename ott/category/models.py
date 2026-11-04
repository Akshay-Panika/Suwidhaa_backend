from django.db import models
from cloudinary.models import CloudinaryField


class Category(models.Model):
    # Manual choices — admin picks one
    CATEGORY_TYPES = (
        ("movie", "Movie"),
        ("cartoon", "Cartoon"),
        ("sport", "Sport"),
        ("sci_fi", "Sci-Fi"),
        ("webseries", "Web Series"),
    )

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )

    image = CloudinaryField(
        "image",
        folder="suwidhaa/ott/categories",
        blank=False,
        null=False,
    )

    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES,
        blank=False,
        null=False,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"