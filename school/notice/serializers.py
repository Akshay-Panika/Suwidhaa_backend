from rest_framework import serializers
from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    display_date = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "audience",
            "assigned_class",
            "attachment",
            "attachment_url",
            "is_pinned",
            "created_by",
            "created_at",
            "display_date",
        ]
        read_only_fields = ["id", "created_at", "display_date", "attachment_url"]

    def get_display_date(self, obj):
        return obj.created_at.strftime("%d %b %Y")

    def get_attachment_url(self, obj):
        if obj.attachment:
            try:
                return obj.attachment.url
            except Exception:
                return None
        return None


class NoticeCreateSerializer(serializers.ModelSerializer):
    """Handles multipart/form-data to accept file uploads."""

    class Meta:
        model = Notice
        fields = [
            "title",
            "description",
            "priority",
            "audience",
            "assigned_class",
            "attachment",
            "is_pinned",
            "created_by",
        ]
        extra_kwargs = {
            "attachment": {"required": False, "allow_null": True},
        }