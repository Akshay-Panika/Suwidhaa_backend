import os

from rest_framework import serializers
from .models import ItServiceCategory


class ItServiceCategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ItServiceCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")
        qs = ItServiceCategory.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A category with this name already exists."
            )
        return value

    def validate(self, attrs):
        is_creating = self.instance is None
        is_default = self.instance.is_default if self.instance else False

        if is_creating:
            name = attrs.get("name", "").strip()
            if name.lower() == ItServiceCategory.ALL_SERVICES_NAME.lower():
                raise serializers.ValidationError(
                    {"name": "This name is reserved for the default category."}
                )
            if not attrs.get("image"):
                raise serializers.ValidationError(
                    {"image": "Image is required for a new category."}
                )
        else:
            if is_default and "name" in attrs:
                if attrs["name"].strip() != self.instance.name:
                    raise serializers.ValidationError(
                        {"name": "The 'All' category cannot be renamed."}
                    )
        return attrs

    # ------------------------------------------------------------------
    # image -> only file name (e.g. "cb1sg3ljdxnwwwibui6l.png")
    # ------------------------------------------------------------------
    @staticmethod
    def _image_name(instance):
        img = getattr(instance, "image", None)
        if not img:
            return None

        # Try Cloudinary public_id first (no extension)
        public_id = getattr(img, "public_id", None)
        # Fallback: url / str
        url = getattr(img, "url", None) or str(img) or (public_id or "")

        if not url:
            return None

        # Strip query string, take last path segment
        return os.path.basename(url.split("?", 1)[0]) or None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = self._image_name(instance)
        data["is_default"] = instance.is_default
        return data