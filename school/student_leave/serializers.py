from rest_framework import serializers
from .models import StudentLeave


class StudentLeaveSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = StudentLeave
        fields = [
            "id",
            "student_id_card",
            "student_name",
            "student_class",
            "school_type",
            "reason_msg",
            "start_date",
            "end_date",
            "image",
            "leave_status",
            "teacher_card_id",
            "teacher_name",
            "created_date",
        ]
        read_only_fields = ["id", "created_date", "leave_status", "teacher_card_id", "teacher_name"]

    def validate(self, attrs):
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be earlier than start date."}
            )
        return attrs


class StudentLeaveApprovalSerializer(serializers.ModelSerializer):
    """Used for teacher approval / rejection / reset to pending."""

    class Meta:
        model = StudentLeave
        fields = ["leave_status", "teacher_card_id", "teacher_name"]

    def validate_leave_status(self, value):
        if value not in ["pending", "approved", "rejected"]:
            raise serializers.ValidationError(
                "leave_status must be one of: 'pending', 'approved', 'rejected'."
            )
        return value