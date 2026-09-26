from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subject_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']