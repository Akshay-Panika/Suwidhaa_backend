# from rest_framework import serializers
# from .models import Subject
# from school.school_type.models import SchoolType
# from school.school_type.serializers import SchoolTypeSerializer

# class SubjectSerializer(serializers.ModelSerializer):
#     # ✅ Write: pass school_id
#     school_id = serializers.PrimaryKeyRelatedField(
#         queryset=SchoolType.objects.all(),
#         source="school",
#         required=True,
#         write_only=True,
#     )
#     # ✅ Read: full school details
#     school = SchoolTypeSerializer(read_only=True)

#     class Meta:
#         model = Subject
#         fields = "__all__"

#     def validate(self, attrs):
#         # Duplicate check
#         school = attrs.get("school", getattr(self.instance, "school", None))
#         name = attrs.get("name", getattr(self.instance, "name", None))

#         if name and school:
#             qs = Subject.objects.filter(name__iexact=name.strip(), school=school)
#             if self.instance:
#                 qs = qs.exclude(pk=self.instance.pk)
#             if qs.exists():
#                 raise serializers.ValidationError(
#                     {"name": f"Subject '{name}' already exists in this school."}
#                 )
#         return attrs

from rest_framework import serializers
from .models import Subject
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer
from school.teacher.models import Teacher

class SubjectSerializer(serializers.ModelSerializer):
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
        source="school",
        required=True,
        write_only=True,
    )
    school = SchoolTypeSerializer(read_only=True)

    teachers = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = "__all__"

    def get_teachers(self, obj):
        all_teachers = Teacher.objects.filter(school=obj.school)
        
        matched_teachers = []
        for t in all_teachers:
            teacher_subjects = t.subjects or []
            if any(str(s).lower() == obj.name.lower() for s in teacher_subjects):
                matched_teachers.append(t)
        
        return [
            {
                "id": t.id,
                "name": f"{t.first_name} {t.last_name}",
                "teacher_id_card": t.teacher_id_card,
                "profile_image": t.teacher_profile.url if t.teacher_profile else None,
            }
            for t in matched_teachers
        ]

    def validate(self, attrs):
        school = attrs.get("school", getattr(self.instance, "school", None))
        name = attrs.get("name", getattr(self.instance, "name", None))

        if name and school:
            qs = Subject.objects.filter(name__iexact=name.strip(), school=school)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"name": f"Subject '{name}' already exists in this school."}
                )
        return attrs