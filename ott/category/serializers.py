from rest_framework import serializers
from .models import Category


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output"""

    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class CategorySerializer(serializers.ModelSerializer):
    image = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")

        # ✅ Reserve "All Content" — cannot be created / renamed to it
        if value.lower() == "all content":
            raise serializers.ValidationError(
                '"All Content" is a reserved category name.'
            )

        # ✅ Case-insensitive uniqueness check
        qs = Category.objects.filter(name__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f'Category "{value}" already exists.'
            )
        return value

    def validate(self, attrs):
        # ✅ Image required only on create
        if self.instance is None and not attrs.get("image"):
            raise serializers.ValidationError(
                {"image": "Image is required to create a category."}
            )
        return attrs