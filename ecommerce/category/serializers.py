from rest_framework import serializers
from .models import EcommerceCategory


class EcommerceCategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=True,
        allow_null=False,
    )

    class Meta:
        model = EcommerceCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = (
            instance.image.url
            if instance.image
            else None
        )
        return data