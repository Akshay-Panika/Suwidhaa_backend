from django.db import models
from cloudinary.models import CloudinaryField


class ItServiceAd(models.Model):
    ad_image = CloudinaryField(
        "ad_image",
        folder="suwidhaa/it_service/ads", # Folder change kar diya hai ads ke liye
        blank=False,
        null=False,
    )
    title = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Optional title for the ad"
    )
    redirect_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL where the user will be redirected on clicking the ad",
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
        db_table = "it_service_ads" # Table ka naam change kar diya
        ordering = ["-id"]

    def __str__(self):
        return f"IT Service Ad {self.id} - {self.title or 'No Title'}"