from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    student_profile = serializers.FileField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Student
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.student_profile:
            data["student_profile"] = instance.student_profile.url
        else:
            data["student_profile"] = None

        return data