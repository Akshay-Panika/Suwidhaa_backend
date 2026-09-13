# college/colleges/serializers.py

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
    booking = serializers.SerializerMethodField()  

    class Meta:
        model = College
        fields = [
            'id', 'name', 'address', 'website', 'contact_number',
            'category', 'logo_url', 'is_recommended',
            'longitude', 'latitude',
            'booking',   
            'images', 'created_at', 'updated_at'
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None

    def get_booking(self, obj):
        user_id = self.context.get('user_id')
        if user_id:
            from college.college_booking.models import CollegeBooking
            return CollegeBooking.objects.filter(
                college_id=obj.id,
                user_id=str(user_id),
                booking=True
            ).exists()
        return False   