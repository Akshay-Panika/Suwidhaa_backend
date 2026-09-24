from rest_framework import serializers
from .models import Student, StudentAttendance


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'student_card_id', 'student_name',
            'student_class', 'school_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceInputSerializer(serializers.Serializer):
    student_card_id = serializers.CharField()
    student_name = serializers.CharField(required=False, allow_blank=True, default='')
    student_class = serializers.CharField(required=False, allow_blank=True, default='')
    school_type = serializers.CharField(required=False, allow_blank=True, default='')
    date = serializers.DateField()
    attendance_status = serializers.ChoiceField(
        choices=['present', 'absent', 'leave'],
        default='present'
    )
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')


class BulkAttendanceSerializer(serializers.Serializer):
    students = AttendanceInputSerializer(many=True)

    def validate_students(self, value):
        if not value:
            raise serializers.ValidationError("Students list khali nahi ho sakti.")
        return value