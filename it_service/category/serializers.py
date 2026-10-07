from rest_framework import serializers
from .models import ItServiceCategory


class ItServiceCategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=True,
        allow_null=False,
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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = (
            instance.image.url
            if instance.image
            else None
        )
        return data