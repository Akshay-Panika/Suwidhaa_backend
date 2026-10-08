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
        # ✅ Explicitly list fields — exclude `category` and `category_name`
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
            "category",           # keep this so POST can still assign category
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            # ✅ Make `category` write-only → accepted on POST/PUT/PATCH,
            # but NOT shown in GET response
            "category": {"write_only": True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # ✅ Only `image` — full Cloudinary URL
        data["image"] = (
            instance.image.url
            if instance.image
            else None
        )

        # ✅ Nested category — replaces both `category` & `category_name`
        data["category_detail"] = (
            ItServiceCategorySerializer(instance.category).data
            if instance.category
            else None
        )

        return data