from django.db import models
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField

from ngo.category.models import NgoCategory


class NgoService(models.Model):
    category = models.ForeignKey(
        NgoCategory,
        on_delete=models.CASCADE,
        related_name="services",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Multiple images (list of URLs)
    images = models.JSONField(
        default=list,
        blank=True,
        help_text="List of image URLs",
    )
    
    # Progress: {target_amount, total_amount, donor}
    progress = models.JSONField(
        default=dict,
        blank=True,
        help_text="Progress info: target_amount, total_amount, donor",
    )
    
    # Keys: [{icon, key, value}, ...]
    keys = models.JSONField(
        default=list,
        blank=True,
        help_text="List of key-value items",
    )
    
    # Choose amounts: [10, 50, 100, ...]
    choose_amount = models.JSONField(
        default=list,
        blank=True,
        help_text="List of quick-select donation amounts",
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