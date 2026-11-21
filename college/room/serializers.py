
from rest_framework import serializers

from .models import Room, RoomImage
from college.colleges.serializers import CollegeSerializer


class RoomImageSerializer(serializers.ModelSerializer):

    url = serializers.SerializerMethodField()

    class Meta:
        model = RoomImage
        fields = [
            "id",
            "url",
            "created_at"
        ]

    def get_url(self, obj):
        return obj.image.url if obj.image else None


class RoomSerializer(serializers.ModelSerializer):

    room_images = RoomImageSerializer(
        many=True,
        read_only=True
    )

    booking = serializers.SerializerMethodField()

    # Complete nested College object
    college = CollegeSerializer(read_only=True)

    # College ID separately
    college_id = serializers.IntegerField(
        source="college.id",
        read_only=True
    )

    class Meta:
        model = Room

        fields = [
            "id",
            "user_id",
            "title",
            "description",
            "address",
            "price",
            "is_booking",
            "booking",
            "longitude",
            "latitude",
            "room_type",
            "contact_number",
            "facilities",
            "near_college",
            "college",
            "college_id",
            "room_images",
            "created_at",
            "updated_at"
        ]

    def get_booking(self, obj):

        user_id = self.context.get("user_id")

        if not user_id:
            return False

        from college.college_booking.models import CollegeBooking

        return CollegeBooking.objects.filter(
            user_id=str(user_id),
            room_id=obj.id,
            booking=True
        ).exists()
