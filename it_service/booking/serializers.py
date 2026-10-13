from rest_framework import serializers

from .models import Booking
from it_service.service.models import ItServiceService


class BookingSerializer(serializers.ModelSerializer):
    service_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "user_id",
            "service",
            "service_detail",
            "full_name",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_service_detail(self, obj):
        service = obj.service
        if not service:
            return None

        return {
            "id": service.id,
            "title": service.title,
            "description": service.description,
            "price": service.price,
            "old_price": service.old_price,
            "image": service.image.url if service.image else None,
            "tech_stack": service.tech_stack,
            "category": (
                {
                    "id": service.category.id,
                    "name": service.category.name,
                    "image": (
                        service.category.image.url
                        if getattr(service.category, "image", None)
                        else None
                    ),
                }
                if service.category
                else None
            ),
        }


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "user_id",
            "service",
            "full_name",
        )

    def validate_user_id(self, value):
        if not value:
            raise serializers.ValidationError("user_id is required")
        return value

    def validate_service(self, value):
        if not ItServiceService.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("Service does not exist")
        return value