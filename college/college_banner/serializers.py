from rest_framework import serializers
from .models import CollegeBanner


class CollegeBannerSerializer(serializers.ModelSerializer):
    banner_image = serializers.FileField(
        required=True,
        allow_null=False
    )

    class Meta:
        model = CollegeBanner
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["banner_image"] = (
            instance.banner_image.url
            if instance.banner_image
            else None
        )

        return data
