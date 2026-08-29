from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    student_profile = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["student_profile"] = instance.student_profile.url if instance.student_profile else None
        return data