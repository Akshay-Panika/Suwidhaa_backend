# college/college_booking/serializers.py

from rest_framework import serializers
from .models import CollegeBooking


class CollegeBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollegeBooking
        fields = [
            'id', 'college_id', 'user_id', 'booking',
            'message',   # ✅ NEW
            'created_at', 'updated_at'
        ]