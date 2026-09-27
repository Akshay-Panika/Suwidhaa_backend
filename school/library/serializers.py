from rest_framework import serializers
from .models import LibraryBook


class LibraryBookSerializer(serializers.ModelSerializer):
    front_image = serializers.SerializerMethodField()
    back_image = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = LibraryBook
        fields = [
            "id",
            "author",
            "book_class",
            "subject",
            "quantity",
            "front_image",
            "back_image",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_front_image(self, obj):
        if obj.front_image:
            return obj.front_image.url
        return None

    def get_back_image(self, obj):
        if obj.back_image:
            return obj.back_image.url
        return None


class LibraryBookCreateUpdateSerializer(serializers.ModelSerializer):
    """Used for POST / PUT / PATCH — accepts image files via multipart."""

    class Meta:
        model = LibraryBook
        fields = [
            "author",
            "book_class",
            "subject",
            "quantity",
            "front_image",
            "back_image",
        ]
        extra_kwargs = {
            "author": {"required": False},
            "book_class": {"required": True},
            "subject": {"required": True},
            "quantity": {"required": False},
            "front_image": {"required": False},
            "back_image": {"required": False},
        }

    def validate_quantity(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value