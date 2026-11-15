from django.db import models
from django.core.validators import RegexValidator
from cloudinary.models import CloudinaryField


class CollegeBanner(models.Model):
    banner_image = CloudinaryField(
        "banner_image",
        folder="suwidhaa/college/banner",
        blank=False,
        null=False,
    )

    # ✅ NEW: YouTube video URL
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$",
                message="Only valid YouTube URLs are allowed.",
            )
        ],
        help_text="YouTube video URL (e.g. https://www.youtube.com/watch?v=XXXX)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"College Banner {self.id}"