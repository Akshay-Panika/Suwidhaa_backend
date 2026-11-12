from django.db import models
from cloudinary.models import CloudinaryField


class Ad(models.Model):
    # ── Ad Title ──
    title = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )

    # ── Banner Image (Cloudinary) ──
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ngo/ads",
        blank=True,
        null=True,
    )

    # ── Video URL (optional — external/Cloudinary) ──
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="External video URL (MP4/HLS) — leave blank for image-only ad",
    )

    # ── Navigate Screen (Flutter route key — manual) ──
    navigate_screen = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Flutter screen route — e.g. 'donate', 'services', 'history'",
    )

    # ── Status ──
    is_active = models.BooleanField(default=True)

    # ── Timestamps ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "NGO Ad"
        verbose_name_plural = "NGO Ads"
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"