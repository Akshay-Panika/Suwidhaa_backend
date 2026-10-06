from rest_framework import serializers
from .models import NgoCategory


class NgoCategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=True,
        allow_null=False,
    )

    class Meta:
        model = NgoCategory
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["image"] = (
            instance.image.url
            if instance.image
            else None
        )

        return data