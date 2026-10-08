from rest_framework import serializers

from .models import ItServiceService
from it_service.category.serializers import ItServiceCategorySerializer


class ItServiceServiceSerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=False,
        allow_null=True,
    )
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    class Meta:
        model = ItServiceService
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Full Cloudinary URL
        data["image"] = (
            instance.image.url
            if instance.image
            else None
        )
        # Flutter alias
        data["imageUrl"] = data["image"]

        # Nested category object
        data["category_detail"] = (
            ItServiceCategorySerializer(instance.category).data
            if instance.category
            else None
        )

        return data