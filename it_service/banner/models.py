from django.db import models
from cloudinary.models import CloudinaryField


class ItServiceBanner(models.Model):
    banner_image = CloudinaryField(
        "banner_image",
        folder="suwidhaa/it_service/banner",
        blank=False,
        null=False,
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional video URL (YouTube, Vimeo, Cloudinary, etc.)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "it_service_banner"
        ordering = ["-id"]

    def __str__(self):
        return f"IT Service Banner {self.id}"