from rest_framework import serializers

from ott.category.models import Category
from ott.category.serializers import CategorySerializer
from .models import Content


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output (same pattern as category app)"""

    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class ContentSerializer(serializers.ModelSerializer):
    # ── Write side: accept category_id (validates category exists) ──
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        error_messages={
            "does_not_exist": "Category with this id does not exist.",
            "incorrect_type": "category_id must be an integer.",
        },
    )

    # ── Read side: return FULL category object ──
    category = CategorySerializer(read_only=True)

    # ── Two thumbnails ──
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Content
        fields = [
            "id",
            "title",
            "description",
            "category_id",          # write only
            "category",             # read only (full object)
            "thumbnail_horizontal",
            "thumbnail_vertical",
            "video_url",
            "video_duration",
            "release_date",
            # ── Boolean flags ──
            "is_family",
            "is_recommended",
            "is_trending",
            "is_something_new",
            "is_lock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_video_url(self, value):
        if value in ("", None):
            return value
        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                "video_url must start with http:// or https://"
            )
        return value

    def validate_video_duration(self, value):
        if value in ("", None):
            return value
        return value.strip()

    def validate_release_date(self, value):
        return value

    # ── Accept "true"/"false"/"1"/"0" strings from form-data ──
    def to_internal_value(self, data):
        # form-data me bool string aati hai — convert karo
        bool_fields = [
            "is_family", "is_recommended",
            "is_trending", "is_something_new", "is_lock",
        ]
        # QueryDict immutable hota hai — copy banao
        if hasattr(data, "copy"):
            data = data.copy()
        for field in bool_fields:
            if field in data:
                val = data.get(field)
                if isinstance(val, str):
                    data[field] = val.strip().lower() in ("true", "1", "yes", "on")
        return super().to_internal_value(data)