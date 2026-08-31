from rest_framework import serializers
from .models import Homework

class HomeworkSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = Homework
        fields = [
            'id',
            'subject_name',
            'subject_topic',
            'issue_date',
            'end_date',
            'image',
            'class_name',
            'teacher_name',
            'teacher_id',
            'school_type',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = instance.image.url if instance.image else None
        return data

    def validate(self, data):
        # Validate that end_date is not before issue_date
        if data.get('end_date') and data.get('issue_date'):
            if data['end_date'] < data['issue_date']:
                raise serializers.ValidationError(
                    "End date cannot be before issue date"
                )
        return data