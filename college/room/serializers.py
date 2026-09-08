# serializers.py
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
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Add user_id field
    owner_name = serializers.CharField(source='user.username', read_only=True)  # Optional: include username

    class Meta:
        model = Room
        fields = [
            'id', 
            'user_id',  # Add user_id to fields
            'owner_name',  # Optional
            'title', 'description', 'address', 'price', 
            'is_booking', 'room_type',
            'contact_number',
            'wifi', 'ac', 'parking', 'security', 'laundry', 'water',
            'near_college',
            'room_images',
            'created_at', 'updated_at'
        ]