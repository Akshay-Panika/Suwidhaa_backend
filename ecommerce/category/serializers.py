from rest_framework import serializers
from .models import EcommerceCategory


class EcommerceCategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=True,
        allow_null=False,
    )

    class Meta:
        model = EcommerceCategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")

        # case-insensitive duplicate check
        qs = EcommerceCategory.objects.filter(title__iexact=value)

        # update ke waqt khud ko exclude karo
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "This category already exists."
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