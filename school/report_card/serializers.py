from rest_framework import serializers
from .models import ReportCard


class ReportCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReportCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCard
        fields = [
            'admin_id', 'student_id', 'school_type', 'class_name',
            'subject_name', 'exam_name', 'sujectmaks_marks',
            'pasingmaks_marks', 'student_marks', 'result', 'description',
        ]