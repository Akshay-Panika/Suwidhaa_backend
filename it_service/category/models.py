from django.db import models
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField


class ItServiceCategory(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )
    image = CloudinaryField(
        "image",
        folder="suwidhaa/it_service/category",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "it_service_category"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_it_service_category_name_ci",
            ),
        ]

    def __str__(self):
        return f"IT Service Category {self.id} - {self.name}"