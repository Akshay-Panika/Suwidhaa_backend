from rest_framework import serializers
from .models import OttAds


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output (same as category/content app)"""

    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class OttAdsSerializer(serializers.ModelSerializer):
    image = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = OttAds
        fields = [
            "id",
            "title",
            "image",
            "video_url",
            "navigate_screen",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_video_url(self, value):
        if value in ("", None):
            return value
        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "video_url must start with http:// or https://"
            )
        return value

    def validate_navigate_screen(self, value):
        if value in ("", None):
            return value
        return value.strip().lower().replace(" ", "_")

    def validate(self, attrs):
        # At least one media (image or video_url) should be present
        image = attrs.get("image", getattr(self.instance, "image", None))
        video_url = attrs.get("video_url", getattr(self.instance, "video_url", None))

        if not image and not video_url:
            raise serializers.ValidationError(
                "At least one of `image` or `video_url` is required."
            )
        return attrs