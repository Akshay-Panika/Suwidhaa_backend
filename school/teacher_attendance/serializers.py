# school/teacher_attendance/serializers.py
from rest_framework import serializers


class AttendanceInputSerializer(serializers.Serializer):
    teacher_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    attendance_status = serializers.ChoiceField(
        choices=['present', 'absent', 'leave'],
        default='present',
    )
    remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, default=''
    )


class BulkAttendanceSerializer(serializers.Serializer):
    teachers = AttendanceInputSerializer(many=True)

    def validate_teachers(self, value):
        if not value:
            raise serializers.ValidationError("Teachers list cannot be empty.")
        return value