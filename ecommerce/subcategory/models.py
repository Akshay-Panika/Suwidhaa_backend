from django.db import models
from cloudinary.models import CloudinaryField
from ecommerce.category.models import EcommerceCategory


class EcommerceSubcategory(models.Model):
    category = models.ForeignKey(
        EcommerceCategory,
        on_delete=models.CASCADE,          # category delete → subcategory auto delete
        related_name="subcategories",
        db_index=True,
    )
    title = models.CharField(max_length=255)
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ecommerce/subcategory",
        blank=False,
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ecommerce_subcategory"
        ordering = ["-id"]
        # same category ke andar title unique ho
        constraints = [
            models.UniqueConstraint(
                fields=["category", "title"],
                name="unique_subcategory_title_per_category",
            )
        ]

    def __str__(self):
        return f"{self.title} (Category: {self.category_id}, ID: {self.id})"