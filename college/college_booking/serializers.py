# college/college_booking/serializers.py

from rest_framework import serializers
from .models import CollegeBooking


# ✅ ADDED: Alag class for Room
class RoomSerializer(serializers.Serializer):
    room_id = serializers.IntegerField(allow_null=True, required=False)
    room_name = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    room_type = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    room_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        allow_null=True, required=False
    )


# ✅ ADDED: Alag class for Tiffin
class TiffinSerializer(serializers.Serializer):
    tiffin_id = serializers.IntegerField(allow_null=True, required=False)
    tiffin_name = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    tiffin_type = serializers.CharField(allow_null=True, required=False, allow_blank=True)
    tiffin_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        allow_null=True, required=False
    )


class CollegeBookingSerializer(serializers.ModelSerializer):
    # ✅ ADDED: nested objects
    room = serializers.SerializerMethodField()
    tiffin = serializers.SerializerMethodField()

    class Meta:
        model = CollegeBooking
        fields = [
            'id', 'college_id', 'user_id', 'booking',
            'message',
            'room',      # ✅ ADDED
            'tiffin',    # ✅ ADDED
            'created_at', 'updated_at'
        ]

    def get_room(self, obj):
        if obj.room_id is None:
            return None
        return {
            "room_id": obj.room_id,
            "room_name": obj.room_name,
            "room_type": obj.room_type,
            "room_amount": str(obj.room_amount) if obj.room_amount is not None else None,
        }

    def get_tiffin(self, obj):
        if obj.tiffin_id is None:
            return None
        return {
            "tiffin_id": obj.tiffin_id,
            "tiffin_name": obj.tiffin_name,
            "tiffin_type": obj.tiffin_type,
            "tiffin_amount": str(obj.tiffin_amount) if obj.tiffin_amount is not None else None,
        }