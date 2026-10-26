# school/teacher_salary/serializers.py
from rest_framework import serializers
from .models import TeacherSalary
from school.teacher.models import Teacher
from school.school_type.models import SchoolType


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


class TeacherSalaryListSerializer(serializers.ModelSerializer):
    """
    Serializer used for the LIST endpoints.
    Shows teacher + school details + salary totals.
    """
    teacher_name = serializers.SerializerMethodField()
    teacher_profile = serializers.SerializerMethodField()
    school_id = serializers.IntegerField(source="school.id", read_only=True)
    school_name = serializers.CharField(source="school.school_name", read_only=True)

    total_salary = serializers.SerializerMethodField()
    paid_amount = serializers.SerializerMethodField()
    pending_amount = serializers.SerializerMethodField()
    last_payment_date = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "teacher_id_card",
            "teacher_name",
            "teacher_profile",
            "school_id",
            "school_name",
            "total_salary",
            "paid_amount",
            "pending_amount",
            "last_payment_date",
        ]

    def get_teacher_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_teacher_profile(self, obj):
        if obj.teacher_profile:
            try:
                return obj.teacher_profile.url
            except Exception:
                return None
        return None

    def get_total_salary(self, obj):
        from django.db.models import Sum
        result = TeacherSalary.objects.filter(teacher=obj).aggregate(Sum("amount"))
        return float(result["amount__sum"] or 0)

    def get_paid_amount(self, obj):
        from django.db.models import Sum
        result = TeacherSalary.objects.filter(teacher=obj).aggregate(Sum("paid_amount"))
        return float(result["paid_amount__sum"] or 0)

    def get_pending_amount(self, obj):
        from django.db.models import Sum
        result = TeacherSalary.objects.filter(teacher=obj).aggregate(Sum("pending_amount"))
        return float(result["pending_amount__sum"] or 0)

    def get_last_payment_date(self, obj):
        last = TeacherSalary.objects.filter(teacher=obj).order_by("-paid_date").first()
        return last.paid_date if last and last.paid_date else None