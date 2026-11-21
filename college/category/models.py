from django.db import models
from cloudinary.models import CloudinaryField


class CollegeCategory(models.Model):
    title = models.CharField(max_length=200)

    image = CloudinaryField(
        "image",
        folder="suwidhaa/college/category",
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "College Category"
        verbose_name_plural = "College Categories"

    def __str__(self):
        return self.title or f"Category {self.id}"