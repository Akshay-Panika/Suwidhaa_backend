from rest_framework import serializers
from .models import StudentLeave

from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer
from school.student.models import Student
from school.student.serializers import StudentSerializer
from school.teacher.models import Teacher
from school.teacher.serializers import TeacherSerializer


class StudentLeaveSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    # ✅ Read-only nested — full models
    school = SchoolTypeSerializer(read_only=True)
    student = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()

    class Meta:
        model = StudentLeave
        fields = [
            "id",
            "student_id_card",     # write + read (needed for create/lookup)
            "reason_msg",
            "start_date",
            "end_date",
            "image",
            "leave_status",        # read-only (from approval)
            "teacher_card_id",     # read-only (set by approval API)
            "created_date",
            # nested
            "school",
            "student",
            "teacher",
        ]
        read_only_fields = [
            "id", "created_date", "leave_status", "teacher_card_id",
            "school", "student", "teacher",
        ]

    # ────── Nested: Full Student (with nested school) ──────
    def get_student(self, obj):
        if not obj.student_id_card:
            return None
        try:
            student = (
                Student.objects
                .select_related("school")
                .get(student_id_card=obj.student_id_card)
            )
            return StudentSerializer(student).data
        except Student.DoesNotExist:
            return None

    # ────── Nested: Full Teacher (with nested school) ──────
    def get_teacher(self, obj):
        if not obj.teacher_card_id:
            return None
        try:
            teacher = (
                Teacher.objects
                .select_related("school")
                .get(teacher_card_id=obj.teacher_card_id)
            )
            return TeacherSerializer(teacher).data
        except Teacher.DoesNotExist:
            return None

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