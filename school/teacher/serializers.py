from rest_framework import serializers
from .models import Teacher
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer


class TeacherSerializer(serializers.ModelSerializer):
    teacher_profile = serializers.FileField(
        required=False,
        allow_null=True,
    )

    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
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