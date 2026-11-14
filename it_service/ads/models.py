from django.db import models
from cloudinary.models import CloudinaryField

class ItServiceAd(models.Model):
    ad_image = CloudinaryField(
        "ad_image",
        folder="suwidhaa/it_service/ads", 
        blank=False,
        null=False,
    )
    title = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Optional title for the ad"
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional video URL (YouTube, Vimeo, Cloudinary, etc.)",
    )
    # 👇 Naya field add kiya hai
    is_home = models.BooleanField(
        default=False,
        help_text="Check if this ad should be displayed on the home screen"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "it_service_ads"
        ordering = ["-id"]

    def __str__(self):
        return f"IT Service Ad {self.id} - {self.title or 'No Title'}"