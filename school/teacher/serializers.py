from rest_framework import serializers
from .models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    teacher_profile = serializers.FileField(
        required=False,
        allow_null=True,
    )
    
    class Meta:
        model = Teacher
        fields = "__all__"
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["teacher_profile"] = instance.teacher_profile.url if instance.teacher_profile else None
        return data