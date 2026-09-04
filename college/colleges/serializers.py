from rest_framework import serializers
from .models import College, CollegeImage

class CollegeImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = CollegeImage
        fields = ['id', 'url', 'created_at']
    
    def get_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CollegeSerializer(serializers.ModelSerializer):
    images = CollegeImageSerializer(many=True, read_only=True)
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = College
        fields = [
            'id', 'name', 'address', 'website', 'contact_number',
            'category', 'logo', 'logo_url', 'is_recommended',
            'images', 'created_at', 'updated_at'
        ]
    
    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None