from django.db import models
from cloudinary.models import CloudinaryField


class EcommerceCategory(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ecommerce/category",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_category"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title} (ID: {self.id})"