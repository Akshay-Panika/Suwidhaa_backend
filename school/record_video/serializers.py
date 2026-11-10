from rest_framework import serializers
from .models import SchoolClass, Subject, RecordVideo

class CloudinaryReadField(serializers.Field):
    def to_representation(self, value):
        return value.url if value else None
    def to_internal_value(self, data):
        return data

class SchoolClassSerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(source='videos.count', read_only=True)
    subject_count = serializers.IntegerField(source='subjects.count', read_only=True) # ✅ Added
    class Meta:
        model = SchoolClass
        fields = ['id', 'name', 'video_count', 'subject_count']

class SubjectSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='school_class.name', read_only=True)
    class Meta:
        model = Subject
        fields = ['id', 'name', 'school_class', 'class_name']
        read_only_fields = ['school_class'] 

class RecordVideoSerializer(serializers.ModelSerializer):
    thumbnail = CloudinaryReadField(required=False, allow_null=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='school_class.name', read_only=True)

    class Meta:
        model = RecordVideo
        fields = [
            'id', 'title', 'school_class', 'class_name', 
            'subject', 'subject_name', 'thumbnail', 'video_url', 
            'duration', 'age_group', 'rating', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']