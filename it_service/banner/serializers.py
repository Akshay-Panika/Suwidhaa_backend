from rest_framework import serializers
from .models import ItServiceBanner


class ItServiceBannerSerializer(serializers.ModelSerializer):
    banner_image = serializers.FileField(
        required=True,
        allow_null=False,
    )
    video_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=500,
    )

    class Meta:
        model = ItServiceBanner
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["banner_image"] = (
            instance.banner_image.url
            if instance.banner_image
            else None
        )
        return data