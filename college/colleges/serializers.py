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

    class Meta:
        model = College
        fields = [
            'id', 'name', 'address', 'website', 
            'category',
            'images', 'created_at', 'updated_at'
        ]