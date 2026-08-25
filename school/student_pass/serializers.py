from rest_framework import serializers
from .models import StudentPass


class StudentPassSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentPass
        fields = [
            'id',
            'student',
            'student_name',
            'student_class',
            'student_id_card',
            'is_active',
            'last_login',
            'created_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_login']
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    
    def get_student_class(self, obj):
        return obj.student.student_class


class StudentPassUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPass
        fields = ['student_id_card', 'is_active']
        extra_kwargs = {
            'student_id_card': {'required': False},
            'is_active': {'required': False}
        }


class StudentPassLoginSerializer(serializers.Serializer):
    student_id_card = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=255)


class StudentPassForgotPasswordSerializer(serializers.Serializer):
    student_id_card = serializers.CharField(max_length=50)
    dob = serializers.DateField()