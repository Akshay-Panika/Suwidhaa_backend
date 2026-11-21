from rest_framework import serializers
from .models import CollegeCategory


class CollegeCategorySerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=200,
    )
    image = serializers.FileField(required=True, allow_null=False)

    class Meta:
        model = CollegeCategory
        fields = "__all__"

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Title must be at least 2 characters."
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = instance.image.url if instance.image else None
        return data