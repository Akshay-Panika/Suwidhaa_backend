# college/tiffins/serializers.py
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

    # ✅ user-wise booking field
    booking = serializers.SerializerMethodField()

    class Meta:
        model = Tiffin
        fields = [
            'id',
            'user_id',
            'title',
            'description',
            'price',

            # ✅ ADDED: latitude + longitude
            'longitude',
            'latitude',

            'is_veg',
            'is_nonveg',
            'is_booking',
            'booking',
            'rating',
            'contact_number',
            'near_college',
            'tiffin_images',
            'created_at',
            'updated_at'
        ]

    def get_booking(self, obj):
        """Check if THIS user has booked THIS tiffin."""
        user_id = self.context.get('user_id')
        if not user_id:
            return False

        from college.college_booking.models import CollegeBooking

        return CollegeBooking.objects.filter(
            user_id=str(user_id),
            tiffin_id=obj.id,
            booking=True
        ).exists()