# school/teacher_salary/serializers.py
from rest_framework import serializers

from school.teacher.models import Teacher
from school.school_type.serializers import SchoolTypeSerializer


class TeacherSalaryListSerializer(serializers.ModelSerializer):
    """
    Teacher model ko return karta hai — exactly teacher app ke
    TeacherSerializer jaisa. Koi salary data nahi.
    """

    teacher_profile = serializers.FileField(
        required=False,
        allow_null=True,
    )

    school_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher._meta.get_field("school").related_model.objects.all(),
        source="school",
        required=False,
        allow_null=True,
        write_only=True,
    )
    school = SchoolTypeSerializer(read_only=True)

    class Meta:
        model = Teacher
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["teacher_profile"] = (
            instance.teacher_profile.url if instance.teacher_profile else None
        )
        return data