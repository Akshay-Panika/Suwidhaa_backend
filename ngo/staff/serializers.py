import re
from rest_framework import serializers
from .models import NgoStaff


class NgoStaffSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=False)

    class Meta:
        model = NgoStaff
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_contact_number(self, value):
        value = value.strip()
        if not re.fullmatch(r"\+?\d{10,15}", value):
            raise serializers.ValidationError(
                "Enter a valid contact number (10–15 digits, optional +)."
            )
        return value

    def validate_address(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Address cannot be empty.")
        return value

    def validate(self, attrs):
        # image required on create
        if self.instance is None and not attrs.get("image"):
            raise serializers.ValidationError({"image": "Image is required."})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = instance.image.url if instance.image else None
        data["role_display"] = instance.get_role_display()
        return data