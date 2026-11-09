from django.db import models
from cloudinary.models import CloudinaryField

from ott.category.models import Category


class Content(models.Model):
    title = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )

    description = models.TextField(
        blank=True,
        null=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="contents",
        db_column="category_id",
    )

    # ── Horizontal thumbnail (OTT banner style 16:9) ──
    thumbnail_horizontal = CloudinaryField(
        "thumbnail_horizontal",
        folder="suwidhaa/ott/content/thumbnails/horizontal",
        blank=True,
        null=True,
    )

    # ── Vertical thumbnail (Reels / Poster style 9:16) ──
    thumbnail_vertical = CloudinaryField(
        "thumbnail_vertical",
        folder="suwidhaa/ott/content/thumbnails/vertical",
        blank=True,
        null=True,
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="External video URL (YouTube, Cloudinary, S3, etc.)",
    )

    video_duration = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="e.g. '02:15:30' or '1h 45m'",
    )

    release_date = models.DateField(
        blank=True,
        null=True,
        help_text="Content release date (YYYY-MM-DD)",
    )

    # ── Boolean flags (all default False) ──
    is_family = models.BooleanField(default=False, help_text="Family-friendly content")
    is_recommended = models.BooleanField(default=False, help_text="Show in Recommended section")
    is_trending = models.BooleanField(default=False, help_text="Show in Trending section")
    is_something_new = models.BooleanField(default=False, help_text="Show in New Arrivals section")
    is_lock = models.BooleanField(default=False, help_text="Locked / Premium content")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Content"
        verbose_name_plural = "Contents"
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["is_trending"]),
            models.Index(fields=["is_recommended"]),
            models.Index(fields=["is_something_new"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.category.name})"