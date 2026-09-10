from rest_framework import serializers
from .models import Banner


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output"""
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class BannerSerializer(serializers.ModelSerializer):
    image = CloudinaryInputField(required=True, allow_null=False)

    class Meta:
        model = Banner
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')