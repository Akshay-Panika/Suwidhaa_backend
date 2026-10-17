from django.db import models
from cloudinary.models import CloudinaryField
from auth.app_auth.models import User


class EcommerceStore(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="store",
        db_index=True,
        help_text="Har user ka sirf ek store ho sakta hai."
    )
    store_name = models.CharField(max_length=255, unique=True)
    store_category = models.CharField(max_length=100, blank=True, null=True) # <-- simple text
    store_address = models.TextField()
    store_phone = models.CharField(max_length=15)
    store_logo = CloudinaryField(
        "store_logo",
        folder="suwidhaa/ecommerce/store",
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_store"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.store_name} (Owner: {self.user.name})"