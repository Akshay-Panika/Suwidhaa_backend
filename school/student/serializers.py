from rest_framework import serializers
from .models import Student
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer


class StudentSerializer(serializers.ModelSerializer):
    student_profile = serializers.FileField(required=False, allow_null=True)

    # ✅ Accept school_id on create/update
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
        source="school",
        required=False,
        allow_null=True,
        write_only=True,
    )
    # ✅ Return full school details on read
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

    def validate(self, attrs):
        # Auto-fill school_type string from selected school (if provided)
        school = attrs.get("school") or getattr(self.instance, "school", None)
        if school and not attrs.get("school_type"):
            attrs["school_type"] = school.school_type
        return attrs