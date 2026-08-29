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
        
        if instance.teacher_profile:
            data["teacher_profile"] = instance.teacher_profile.url
        else:
            data["teacher_profile"] = None
            
        return data
    
    def validate_teacher_id_card(self, value):
        """Validate that teacher_id_card is unique if provided"""
        if value:
            instance = self.instance
            if Teacher.objects.exclude(pk=instance.pk if instance else None).filter(teacher_id_card=value).exists():
                raise serializers.ValidationError("Teacher ID Card already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email format if provided"""
        if value:
            instance = self.instance
            if Teacher.objects.exclude(pk=instance.pk if instance else None).filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            if not value.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
        return value