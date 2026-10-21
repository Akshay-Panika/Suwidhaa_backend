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

    def validate_latitude(self, value):
        if value is not None and not (-90 <= float(value) <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        if value is not None and not (-180 <= float(value) <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value