from rest_framework import serializers
from .models import Room, RoomImage

class RoomImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomImage
        fields = ['id', 'url', 'created_at']
    
    def get_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RoomSerializer(serializers.ModelSerializer):
    room_images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'title', 'description', 'address', 'price', 
            'is_booking', 'room_type',
            'wifi', 'ac', 'parking', 'security', 'laundry', 'water',
            'near_college',
            'room_images',
            'created_at', 'updated_at'
        ]