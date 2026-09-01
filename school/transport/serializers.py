# school/transport/serializers.py
from rest_framework import serializers
from .models import Transport, TransportStudent

class TransportStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportStudent
        fields = [
            'id', 'student_name', 'student_id', 
            'pickup_time', 'drop_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TransportSerializer(serializers.ModelSerializer):
    driver_image = serializers.FileField(required=False, allow_null=True)
    students = TransportStudentSerializer(many=True, read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Transport
        fields = [
            'id', 'transport_type', 'school_type', 'vehicle_number',
            'driver_name', 'driver_number', 'driver_image',
            'capacity', 'route_name',
            'students', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.students.count()
    
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
        
        return data


class TransportListSerializer(serializers.ModelSerializer):
    """List serializer with full student data"""
    driver_image_url = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    students = TransportStudentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Transport
        fields = [
            'id', 'transport_type', 'school_type', 'vehicle_number', 
            'driver_name', 'driver_number', 'driver_image_url',
            'capacity', 'route_name', 
            'students', 'student_count'
        ]
    
    def get_driver_image_url(self, obj):
        return obj.driver_image.url if obj.driver_image else None
    
    def get_student_count(self, obj):
        return obj.students.count()


class TransportDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with students data"""
    driver_image = serializers.FileField(required=False, allow_null=True)
    students = TransportStudentSerializer(many=True, read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Transport
        fields = [
            'id', 'transport_type', 'school_type', 'vehicle_number',
            'driver_name', 'driver_number', 'driver_image',
            'capacity', 'route_name',
            'students', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.students.count()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        if instance.driver_image:
            data['driver_image'] = instance.driver_image.url if hasattr(instance.driver_image, 'url') else None
        
        return data