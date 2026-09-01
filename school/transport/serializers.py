# school/transport/serializers.py
from rest_framework import serializers
from .models import Transport

class TransportSerializer(serializers.ModelSerializer):
    driver_image = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = Transport
        fields = [
            'id', 'transport_type', 'school_type', 'vehicle_number',
            'driver_name', 'driver_number', 'driver_image',
            'students_data', 'capacity', 'route_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_students_data(self, value):
        """Validate students data structure"""
        if not isinstance(value, list):
            raise serializers.ValidationError("students_data must be a list")
        
        for student in value:
            if not isinstance(student, dict):
                raise serializers.ValidationError("Each student must be a dictionary")
            
            # Check required fields
            required_fields = ['student_name', 'student_id']
            for field in required_fields:
                if field not in student:
                    raise serializers.ValidationError(f"'{field}' is required for each student")
        
        return value
    
    def validate_vehicle_number(self, value):
        """Validate vehicle number"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Valid vehicle number is required")
        return value.upper().strip()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Get driver image URL
        if instance.driver_image:
            data['driver_image'] = instance.driver_image.url if hasattr(instance.driver_image, 'url') else None
        
        # Add student count
        data['student_count'] = len(instance.students_data or [])
        
        return data


class TransportListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list view"""
    student_count = serializers.SerializerMethodField()
    driver_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Transport
        fields = [
            'id', 'transport_type', 'school_type', 'vehicle_number', 
            'driver_name', 'driver_number', 'driver_image_url',
            'capacity', 'student_count', 'is_active', 'route_name'
        ]
    
    def get_student_count(self, obj):
        return len(obj.students_data or [])
    
    def get_driver_image_url(self, obj):
        return obj.driver_image.url if obj.driver_image else None