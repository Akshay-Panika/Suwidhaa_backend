from rest_framework import serializers
from .models import Room, RoomImage

class RoomImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'image_url', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RoomSerializer(serializers.ModelSerializer):
    room_images = RoomImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'title', 'description', 'address', 'price', 
            'is_booking',
            'wifi', 'ac', 'parking', 'security', 'laundry', 'water',
            'near_college',
            'room_images',
            'created_at', 'updated_at'
        ]


class RoomCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update with image handling"""
    images = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True,
        help_text="Multiple image files"
    )
    
    class Meta:
        model = Room
        fields = [
            'id', 'title', 'description', 'address', 'price', 
            'is_booking',
            'wifi', 'ac', 'parking', 'security', 'laundry', 'water',
            'near_college',
            'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        images = validated_data.pop('images', [])
        
        # Create room
        room = Room.objects.create(**validated_data)
        
        # Handle images if you're using RoomImage model
        for image in images:
            RoomImage.objects.create(
                room=room,
                image=image
            )
        
        return room
    
    def update(self, instance, validated_data):
        images = validated_data.pop('images', None)
        
        # Update room fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle images if provided
        if images is not None:
            # Delete old images
            instance.room_images.all().delete()
            # Add new images
            for image in images:
                RoomImage.objects.create(
                    room=instance,
                    image=image
                )
        
        return instance