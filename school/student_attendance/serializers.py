from rest_framework import serializers


class AttendanceInputSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(required=True)
    date = serializers.DateField(required=True)
    attendance_status = serializers.ChoiceField(
        choices=['present', 'absent', 'leave'],
        default='present'
    )
    remarks = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, default=''
    )


class BulkAttendanceSerializer(serializers.Serializer):
    students = AttendanceInputSerializer(many=True)

    def validate_students(self, value):
        if not value:
            raise serializers.ValidationError("Students list cannot be empty.")
        return value