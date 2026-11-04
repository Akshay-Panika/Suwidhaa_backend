from rest_framework import serializers
from .models import Banner


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output"""
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class BannerSerializer(serializers.ModelSerializer):
    image = CloudinaryInputField(required=True, allow_null=False)

    video_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Banner
        fields = "__all__"   # ✅ is_active auto-drops because the field no longer exists
        read_only_fields = ("id", "is_play", "created_at", "updated_at")