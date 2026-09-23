from rest_framework import serializers

from .models import TeacherSalary


class TeacherSalarySerializer(serializers.ModelSerializer):
    teacher_id_card = serializers.CharField(source="teacher.teacher_id_card", read_only=True)
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherSalary
        fields = [
            "id",
            "teacher",
            "teacher_id_card",
            "teacher_name",
            "month",
            "year",
            "payment_method",
            "amount",
            "paid_amount",
            "pending_amount",
            "status",
            "paid_date",
            "remark",
            "created_at",
        ]
        read_only_fields = ("pending_amount", "created_at", "updated_at")
        extra_kwargs = {"teacher": {"write_only": True}}

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"