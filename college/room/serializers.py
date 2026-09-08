from rest_framework import serializers
from .models import Room, RoomImage
from django.contrib.auth import get_user_model

User = get_user_model()

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
    user_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id', 
            'user_id',
            'user_name',
            'title', 
            'description', 
            'address', 
            'price', 
            'is_booking', 
            'room_type',
            'contact_number',
            'wifi', 
            'ac', 
            'parking', 
            'security', 
            'laundry', 
            'water',
            'near_college',
            'room_images',
            'created_at', 
            'updated_at'
        ]
    
    def get_user_id(self, obj):
        if obj.user:
            return obj.user.id
        return None
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.username
        return None