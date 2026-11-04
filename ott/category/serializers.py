from rest_framework import serializers
from .models import Category


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output"""

    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class CategorySerializer(serializers.ModelSerializer):
    # ✅ required=True on create, optional on update (handled via __init__)
    image = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On create → image mandatory
        if self.instance is None:
            self.fields["image"].required = True
            self.fields["image"].allow_null = False

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")

        if value.lower() == "all content":
            raise serializers.ValidationError(
                '"All Content" is a reserved category name.'
            )

        qs = Category.objects.filter(name__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f'Category "{value}" already exists.'
            )
        return value