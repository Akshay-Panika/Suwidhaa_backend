from rest_framework import serializers
from .models import Student
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer


class StudentSerializer(serializers.ModelSerializer):
    student_profile = serializers.FileField(required=False, allow_null=True)

    # ✅ Write: pass school_id
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
        source="school",
        required=False,
        allow_null=True,
        write_only=True,
    )
    # ✅ Read: full school details
    school = SchoolTypeSerializer(read_only=True)

    class Meta:
        model = Student
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["student_profile"] = (
            instance.student_profile.url if instance.student_profile else None
        )
        return data