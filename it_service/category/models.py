from django.db import models
from django.db.models.functions import Lower
from cloudinary.models import CloudinaryField


class ItServiceCategory(models.Model):
    # System Category Constants
    ALL_SERVICES_ID = 0
    ALL_SERVICES_NAME = "All Services"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    image = CloudinaryField(
        "image",
        folder="suwidhaa/it_service/category",
        blank=True,
        null=True,
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

    @property
    def is_default(self) -> bool:
        return self.pk == self.ALL_SERVICES_ID

    def save(self, *args, **kwargs):
        # Protect default category name
        if self.pk == self.ALL_SERVICES_ID:
            self.name = self.ALL_SERVICES_NAME
            # Agar record exist nahi karta to insert force karo
            if not type(self).objects.filter(pk=self.ALL_SERVICES_ID).exists():
                kwargs["force_insert"] = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Default category delete nahi ho sakti
        if self.is_default:
            raise ValueError("The 'All Services' category cannot be deleted.")
        return super().delete(*args, **kwargs)

    def __str__(self):
        return f"IT Service Category {self.id} - {self.name}"