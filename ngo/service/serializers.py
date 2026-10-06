from rest_framework import serializers
from .models import NgoService
from ngo.category.models import NgoCategory


class NgoServiceSerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=True,
        allow_null=False,
    )

    category = serializers.PrimaryKeyRelatedField(
        queryset=NgoCategory.objects.all(),
        required=True,
    )

    class Meta:
        model = NgoService
        fields = "__all__"

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Service name cannot be empty.")

        qs = NgoService.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "A service with this name already exists."
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