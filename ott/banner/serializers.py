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

    # ✅ Optional video URL — accepts "", null, or a valid URL
    video_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    class Meta:
        model = Banner
        fields = "__all__"
        # ✅ is_play is managed by the model's save() — never accepted from client
        read_only_fields = ("id", "is_play", "created_at", "updated_at")