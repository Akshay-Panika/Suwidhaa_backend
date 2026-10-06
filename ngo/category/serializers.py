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

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")

        # Exclude current instance (during update) from duplicate check
        qs = NgoCategory.objects.filter(name__iexact=value)
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