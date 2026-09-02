from rest_framework import serializers
from .models import College, CollegeImage

class CollegeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeImage
        fields = ['id', 'image', 'created_at']


class CollegeSerializer(serializers.ModelSerializer):
    images = CollegeImageSerializer(many=True, read_only=True)

    class Meta:
        model = College
        fields = ['id', 'name', 'address', 'website', 'images', 'created_at', 'updated_at']