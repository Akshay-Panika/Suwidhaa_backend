from rest_framework import serializers
from .models import Subject
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer
from school.teacher.models import Teacher
from school.teacher.serializers import TeacherSerializer  # ✅ Import TeacherSerializer

class SubjectSerializer(serializers.ModelSerializer):
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
        source="school",
        required=True,
        write_only=True,
    )
    school = SchoolTypeSerializer(read_only=True)

    # ✅ Full teacher data using TeacherSerializer
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
        
        # ✅ Use TeacherSerializer to return full model data
        return TeacherSerializer(matched_teachers, many=True, context=self.context).data

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