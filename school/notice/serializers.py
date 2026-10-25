from rest_framework import serializers
from school.school_type.models import SchoolType  # ✅ Changed this line
from .models import Notice



class SchoolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolType
        fields = "__all__"


class NoticeSerializer(serializers.ModelSerializer):
    display_date = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()
    school = SchoolTypeSerializer(read_only=True)

    class Meta:
        model = Notice
        fields = [
            "id",
            "school",
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
        read_only_fields = [
            "id",
            "created_at",
            "display_date",
            "attachment_url",
        ]

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
    school_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Notice
        fields = [
            "school_id",
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

    def validate_school_id(self, value):
        if not SchoolType.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                f"School with id {value} not found"
            )
        return value

    def create(self, validated_data):
        school_id = validated_data.pop("school_id")
        school = SchoolType.objects.get(pk=school_id)
        return Notice.objects.create(school=school, **validated_data)