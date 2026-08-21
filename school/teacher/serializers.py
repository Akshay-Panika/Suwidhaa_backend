from rest_framework import serializers
from .models import Teacher
import re


class TeacherSerializer(serializers.ModelSerializer):
    teacher_profile = serializers.FileField(
        required=False,
        allow_null=True,
    )
    
    # Add read-only fields to prevent modification if needed
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Teacher
        fields = "__all__"
        # Optionally specify which fields can be updated
        # extra_kwargs = {
        #     'teacher_id': {'required': False},
        #     'first_name': {'required': True},
        #     'last_name': {'required': True},
        # }
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.teacher_profile:
            data["teacher_profile"] = instance.teacher_profile.url
        else:
            data["teacher_profile"] = None
            
        return data
    
    def validate_teacher_id(self, value):
        """Validate that teacher_id is unique if provided"""
        if value:
            instance = self.instance
            # Check uniqueness excluding current instance
            queryset = Teacher.objects.all()
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.filter(teacher_id=value).exists():
                raise serializers.ValidationError("Teacher ID already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email format and uniqueness if provided"""
        if value:
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                raise serializers.ValidationError("Invalid email format.")
            
            # Check uniqueness
            instance = self.instance
            queryset = Teacher.objects.all()
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value:
            # Remove any spaces or special characters for validation
            clean_phone = re.sub(r'[\s\-\(\)\+]', '', value)
            if not clean_phone.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
            
            # Validate length (adjust as needed)
            if len(clean_phone) < 10 or len(clean_phone) > 15:
                raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value
    
    def validate_alt_phone(self, value):
        """Validate alternate phone number format"""
        if value:
            clean_phone = re.sub(r'[\s\-\(\)\+]', '', value)
            if not clean_phone.isdigit():
                raise serializers.ValidationError("Alternate phone number must contain only digits.")
            
            if len(clean_phone) < 10 or len(clean_phone) > 15:
                raise serializers.ValidationError("Alternate phone number must be between 10 and 15 digits.")
        return value
    
    def validate_salary(self, value):
        """Validate salary is not negative"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Salary cannot be negative.")
        return value
    
    def validate_experience(self, value):
        """Validate experience is not negative"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Experience cannot be negative.")
        return value
    
    def validate_subjects(self, value):
        """Validate subjects is a list"""
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Subjects must be a list.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Check if at least first_name and last_name are provided for creation
        if not self.instance:  # Creation
            if not data.get('first_name'):
                raise serializers.ValidationError({"first_name": "First name is required."})
            if not data.get('last_name'):
                raise serializers.ValidationError({"last_name": "Last name is required."})
        
        # Validate date fields
        if data.get('dob') and data.get('join_date'):
            if data['dob'] > data['join_date']:
                raise serializers.ValidationError("Date of birth cannot be after join date.")
        
        return data