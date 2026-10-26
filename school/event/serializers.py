from rest_framework import serializers
from .models import SchoolEvent
from school.school_type.models import SchoolType

class SchoolEventSerializer(serializers.ModelSerializer):
    display_date = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    
    # Read-only fields to show school details
    school_name = serializers.CharField(source="school.school_name", read_only=True)
    school_code = serializers.CharField(source="school.school_code", read_only=True)

    class Meta:
        model = SchoolEvent
        fields = [
            "id",
            "school",          # Accepts ID on write
            "school_name",     # Read-only
            "school_code",     # Read-only
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
        read_only_fields = ["id", "created_at", "display_date", "banner_url", "school_name", "school_code"]

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
    """Used specifically for creating events (handles multipart/form-data for images)"""

    class Meta:
        model = SchoolEvent
        fields = [
            "school",
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

    def validate_school(self, value):
        if not SchoolType.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("School does not exist.")
        return value