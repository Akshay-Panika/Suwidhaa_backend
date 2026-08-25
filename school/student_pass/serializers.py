from rest_framework import serializers
from .models import StudentPass
from school.student.models import Student


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
            'password',
            'is_active',
            'last_login',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_login', 'student']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    
    def get_student_class(self, obj):
        return obj.student.student_class
    
    def update(self, instance, validated_data):
        # Update student_id_card if provided
        student_id_card = validated_data.get('student_id_card')
        if student_id_card:
            if StudentPass.objects.exclude(id=instance.id).filter(student_id_card=student_id_card).exists():
                raise serializers.ValidationError({"student_id_card": "This student ID card already exists"})
            instance.student_id_card = student_id_card
        
        # Update password if provided
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        
        # Update is_active
        is_active = validated_data.get('is_active')
        if is_active is not None:
            instance.is_active = is_active
        
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)  # Remove password from response
        return data


class StudentPassLoginSerializer(serializers.Serializer):
    student_id_card = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=255)