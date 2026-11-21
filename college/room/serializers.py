from rest_framework import serializers
from .models import Room, RoomImage


class RoomImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = RoomImage
        fields = ["id", "url", "created_at"]

    def get_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RoomSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source="college.name", read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "college",
            "college_name",
            "room_number",
            "room_type",
            "capacity",
            "rent_or_fee",
            "is_available",
            "description",
            "images",
            "created_at",
            "updated_at",
        ]