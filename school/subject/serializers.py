from rest_framework import serializers
from .models import Subject
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer

class SubjectSerializer(serializers.ModelSerializer):
    # ✅ Write: pass school_id
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
        source="school",
        required=True,
        write_only=True,
    )
    # ✅ Read: full school details
    school = SchoolTypeSerializer(read_only=True)

    class Meta:
        model = Subject
        fields = "__all__"

    def validate(self, attrs):
        # Duplicate check
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