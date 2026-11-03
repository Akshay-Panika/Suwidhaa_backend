from rest_framework import serializers
from .models import StudentPass

class StudentPassSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    student_id_card = serializers.CharField(read_only=True)
    
    class Meta:
        model = StudentPass
        fields = ['id', 'student', 'student_name', 'student_class', 'student_id_card', 'is_active', 'last_login', 'created_at']
        read_only_fields = ['created_at', 'updated_at', 'last_login', 'student_id_card']
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    
    def get_student_class(self, obj):
        return obj.student.student_class

class StudentPassUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPass
        fields = ['is_active']
        extra_kwargs = {'is_active': {'required': False}}

class StudentPassLoginSerializer(serializers.Serializer):
    student_id_card = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=255)

# Step 1: Request OTP for Forgot Password
class RequestForgotPasswordOtpSerializer(serializers.Serializer):
    student_id_card = serializers.CharField(max_length=50)
    dob = serializers.DateField()

# Step 2: Verify OTP & Set Custom New Password
class VerifyOtpAndResetPasswordSerializer(serializers.Serializer):
    student_id_card = serializers.CharField(max_length=50)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=255, min_length=6)