from django.db import models
from cloudinary.models import CloudinaryField


class Cartoon(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    # ✅ NEW — category FK (same target as Movie)
    category = models.ForeignKey(
        "ott_category.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cartoons",
        help_text='NULL → appears only in "All Content" (virtual).',
    )

    thumbnail_horizontal = CloudinaryField(
        "thumbnail_horizontal",
        folder="suwidhaa/ott/cartoons/horizontal",
        blank=True, null=True,
    )
    thumbnail_vertical = CloudinaryField(
        "thumbnail_vertical",
        folder="suwidhaa/ott/cartoons/vertical",
        blank=True, null=True,
    )

    content_type = models.CharField(
        max_length=50,
        default="cartoon",
        editable=False,
    )

    release_date = models.DateField()
    language = models.CharField(max_length=100)
    duration = models.CharField(max_length=50, help_text="e.g., 2h 15m or 45m")
    video_url = models.URLField(max_length=500)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    is_trending = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Cartoon"
        verbose_name_plural = "Cartoons"

    def __str__(self):
        return f"{self.title} ({self.content_type})"