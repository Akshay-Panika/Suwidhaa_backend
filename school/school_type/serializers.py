from rest_framework import serializers
from .models import SchoolType


class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = "__all__"

    def validate_school_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("School name is required")
        return value.strip()