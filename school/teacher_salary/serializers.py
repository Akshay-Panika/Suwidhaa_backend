from rest_framework import serializers

from .models import (
    TeacherSalary,
    TeacherExtraSalary,
    TeacherSalaryRequest,
    TeacherPendingSalary,
    TeacherBankDetail,
)


class TeacherSalarySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherSalary
        fields = "__all__"
        read_only_fields = ("pending_amount", "created_at", "updated_at")

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"


class TeacherExtraSalarySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherExtraSalary
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"


class TeacherSalaryRequestSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherSalaryRequest
        fields = "__all__"
        read_only_fields = ("date", "status", "created_at", "updated_at")

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"


class TeacherPendingSalarySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPendingSalary
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"


class TeacherBankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherBankDetail
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")