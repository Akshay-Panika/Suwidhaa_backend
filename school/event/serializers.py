from rest_framework import serializers
from .models import SchoolEvent


class SchoolEventSerializer(serializers.ModelSerializer):
    display_date = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()

    class Meta:
        model = SchoolEvent
        fields = [
            "id",
            "title",
            "description",
            "category",
            "venue",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "organizer",
            "audience",
            "status",
            "banner",
            "banner_url",
            "is_pinned",
            "created_at",
            "display_date",
        ]
        read_only_fields = ["id", "created_at", "display_date", "banner_url"]

    def get_display_date(self, obj):
        return obj.created_at.strftime("%d %b %Y")

    def get_banner_url(self, obj):
        if obj.banner:
            try:
                return obj.banner.url
            except Exception:
                return None
        return None


class SchoolEventCreateSerializer(serializers.ModelSerializer):
    """Handles multipart/form-data to accept banner upload."""

    class Meta:
        model = SchoolEvent
        fields = [
            "title",
            "description",
            "category",
            "venue",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "organizer",
            "audience",
            "status",
            "banner",
            "is_pinned",
        ]
        extra_kwargs = {
            "banner": {"required": False, "allow_null": True},
        }