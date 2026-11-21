# college/rooms/serializers.py

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

    # ✅ user-wise booking field
    booking = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = [
            'id',
            'user_id',
            'title',
            'description',
            'address',
            'price',
            'is_booking',
            'booking',          # ✅ user-wise flag
            'longitude',
            'latitude',
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

    def get_booking(self, obj):
        """Check if THIS user has booked THIS room."""
        user_id = self.context.get('user_id')
        if not user_id:
            return False

        from college.college_booking.models import CollegeBooking

        return CollegeBooking.objects.filter(
            user_id=str(user_id),
            room_id=obj.id,         # ✅ match room_id
            booking=True
        ).exists()