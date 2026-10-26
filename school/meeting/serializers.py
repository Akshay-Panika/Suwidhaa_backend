from rest_framework import serializers
from .models import Meeting
from school.school_type.models import SchoolType

class MeetingSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.school_name", read_only=True)

    class Meta:
        model = Meeting
        fields = [
            'id', 
            'school',          # Accepts ID on write
            'school_name',     # Read-only
            'title', 
            'date', 
            'time',
            'for_meeting', 
            'class_name', 
            'zoom_url',
            'created_at', 
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'school_name']

    def validate_school(self, value):
        if value and not SchoolType.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError("School does not exist.")
        return value