from django.db import models
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField


class NgoService(models.Model):
    name = models.CharField(max_length=255)
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ngo/service",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_ngo_service_name_ci",
            ),
        ]

    def __str__(self):
        return f"NGO Service {self.id} - {self.name}"