from rest_framework import serializers
from .models import EcommerceBanner


class EcommerceBannerSerializer(serializers.ModelSerializer):
    banner_image = serializers.FileField(
        required=True,
        allow_null=False,
    )

    class Meta:
        model = EcommerceBanner
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