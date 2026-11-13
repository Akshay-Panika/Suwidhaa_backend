from rest_framework import serializers
from .models import ItServiceService
from it_service.category.serializers import ItServiceCategorySerializer

class ItServiceServiceSerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ItServiceService
        fields = (
            "id",
            "image",
            "title",
            "description",
            "price",
            "old_price",
            "tech_stack",
            "created_at",
            "updated_at",
            "category",           
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            "category": {"write_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Full Cloudinary URL
        try:
            data["image"] = instance.image.url if instance.image else None
        except Exception:
            data["image"] = None

        # Nested category detail
        data["category_detail"] = (
            ItServiceCategorySerializer(instance.category).data
            if instance.category
            else None
        )

        return data