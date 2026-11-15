from rest_framework import serializers
from .models import CollegeBanner


class CollegeBannerSerializer(serializers.ModelSerializer):
    banner_image = serializers.FileField(
        required=True,
        allow_null=False
    )

    # ✅ NEW: video_url field
    video_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=500,
    )

    class Meta:
        model = CollegeBanner
        fields = "__all__"

    def validate_video_url(self, value):
        """Optional: extra validation for YouTube URLs."""
        if not value:
            return value

        allowed_hosts = ["youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"]
        from urllib.parse import urlparse

        host = urlparse(value).netloc.lower()
        if host not in allowed_hosts:
            raise serializers.ValidationError(
                "Only YouTube video URLs are allowed."
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["banner_image"] = (
            instance.banner_image.url
            if instance.banner_image
            else None
        )

        # video_url already a string — no transformation needed
        data["video_url"] = instance.video_url or None

        return data