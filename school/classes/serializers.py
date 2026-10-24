# school/classes/serializers.py
from rest_framework import serializers

from .models import Class
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer
from school.teacher.models import Teacher
from school.teacher.serializers import TeacherSerializer


class ClassSerializer(serializers.ModelSerializer):
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

    # ✅ Write: pass teacher_id when assigning class teacher
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        source="class_teacher",
        required=False,
        allow_null=True,
        write_only=True,
    )
    # ✅ Read: full teacher details
    class_teacher = TeacherSerializer(read_only=True)

    class Meta:
        model = Class
        fields = "__all__"

    def validate(self, attrs):
        # teacher must belong to the same school as the class
        school = attrs.get("school", getattr(self.instance, "school", None))
        teacher = attrs.get(
            "class_teacher", getattr(self.instance, "class_teacher", None)
        )

        if teacher and school and teacher.school_id != school.id:
            raise serializers.ValidationError(
                {
                    "teacher_id": (
                        "Selected teacher does not belong to this class's school."
                    )
                }
            )

        # prevent duplicate class_name within the same school
        class_name = attrs.get(
            "class_name", getattr(self.instance, "class_name", None)
        )
        if class_name and school:
            qs = Class.objects.filter(class_name=class_name, school=school)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "class_name": (
                            f"Class '{class_name}' already exists for this school."
                        )
                    }
                )

        return attrs