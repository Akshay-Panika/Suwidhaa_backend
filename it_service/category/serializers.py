from rest_framework import serializers
from .models import ItServiceCategory


class ItServiceCategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=False,
        allow_null=True,
    )

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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # ---- IMAGE: return NAME ONLY (string), not URL / object ----
        image = getattr(instance, "image", None)
        if not image:
            data["image"] = None
        else:
            # CloudinaryField:
            #   image.name      -> public_id, e.g. "suwidhaa/it_service/category/abc123"
            #   str(image)      -> same as image.name
            #   image.url       -> full https:// URL
            #   basename(name)  -> only the file name without folder
            #
            # Change the next line if you want a different "name" style:
            data["image"] = image.name          # public_id / name
            # data["image"] = os.path.basename(image.name)   # filename only
            # data["image"] = image.url                      # full URL

        data["is_default"] = instance.is_default
        return data