from rest_framework import serializers
from .models import TeacherPass
from school.school_type.serializers import SchoolTypeSerializer # ✅ Import add kiya


class TeacherPassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_class = serializers.SerializerMethodField()
    teacher_id_card = serializers.CharField(read_only=True)
    
    # ✅ Ye line teacher ke model se school ka pura data uthayegi
    school = SchoolTypeSerializer(source='teacher.school', read_only=True)

    class Meta:
        model = TeacherPass
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "teacher_class",
            "teacher_id_card",
            "school", # ✅ Fields me add kiya
            "is_active",
            "last_login",
            "created_at",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "last_login",
            "teacher_id_card",
        ]

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    def get_teacher_class(self, obj):
        return obj.teacher.subjects if obj.teacher.subjects else "N/A"


class TeacherPassUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherPass
        fields = ["is_active"]
        extra_kwargs = {"is_active": {"required": False}}


class TeacherPassLoginSerializer(serializers.Serializer):
    teacher_id_card = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=255)


# ---------- FORGOT PASSWORD (OTP FLOW) ----------
class TeacherRequestForgotPasswordOtpSerializer(serializers.Serializer):
    teacher_id_card = serializers.CharField(max_length=50)
    dob = serializers.DateField()


class TeacherVerifyOtpAndResetPasswordSerializer(serializers.Serializer):
    teacher_id_card = serializers.CharField(max_length=50)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=255, min_length=6)