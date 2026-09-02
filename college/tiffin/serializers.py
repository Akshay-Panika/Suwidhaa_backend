from rest_framework import serializers
from .models import Tiffin, TiffinImage

class TiffinImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = TiffinImage
        fields = ['id', 'url', 'created_at']
    
    def get_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class TiffinSerializer(serializers.ModelSerializer):
    tiffin_images = TiffinImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tiffin
        fields = [
            'id', 'title', 'description', 'price',
            'is_veg', 'is_nonveg',
            'is_booking', 'rating',
            'near_college',
            'tiffin_images',
            'created_at', 'updated_at'
        ]