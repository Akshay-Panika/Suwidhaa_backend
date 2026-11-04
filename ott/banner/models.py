from django.db import models
from cloudinary.models import CloudinaryField


class Banner(models.Model):
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ott/banners",
        blank=False,
        null=False,
    )

    # ✅ NEW: optional video URL
    video_url = models.URLField(
        blank=True,
        null=True,
    )

    # ✅ NEW: auto-managed flag
    #    True  → video_url exists
    #    False → video_url empty / null
    is_play = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # ✅ Normalise: "" → None, strip whitespace
        url = (self.video_url or "").strip()
        self.video_url = url or None

        # ✅ Auto-derive is_play
        self.is_play = bool(url)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Banner #{self.pk}"