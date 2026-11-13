from django.db import models
from cloudinary.models import CloudinaryField
from it_service.category.models import ItServiceCategory

class ItServiceService(models.Model):
    category = models.ForeignKey(
        ItServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.CharField(max_length=50, blank=True, default="")
    old_price = models.CharField(max_length=50, blank=True, default="")
    image = CloudinaryField(
        "image",
        folder="suwidhaa/it_service/service",
        blank=True,
        null=True,
    )
    tech_stack = models.JSONField(
        default=list,
        blank=True,
        help_text='["Flutter","Firebase","Node.js"]',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "it_service_service"
        ordering = ["-id"]

    def __str__(self):
        return f"IT Service {self.id} - {self.title}"