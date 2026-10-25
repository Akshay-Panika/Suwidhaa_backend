from rest_framework import serializers
from .models import Transport, TransportStudent
from school.student.models import Student
from school.student.serializers import StudentSerializer
from school.school_type.models import SchoolType
from school.school_type.serializers import SchoolTypeSerializer

class TransportStudentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True) 
    
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source="student",
        write_only=True
    )

    class Meta:
        model = TransportStudent
        fields = ['id', 'student', 'student_id', 'address', 'pickup_time', 'drop_time', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TransportSerializer(serializers.ModelSerializer):
    driver_image = serializers.FileField(required=False, allow_null=True)
    
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=SchoolType.objects.all(),
        source="school",
        required=False,
        allow_null=True,
        write_only=True,
    )
    school = SchoolTypeSerializer(read_only=True)
    
    students = TransportStudentSerializer(source='assigned_students', many=True, read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Transport
        fields = [
            'id', 'school', 'school_id', 'transport_type', 'vehicle_number',
            'driver_name', 'driver_number', 'driver_image',
            'capacity', 'route_name', 'students', 'student_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_student_count(self, obj):
        return obj.assigned_students.count()
    
    def validate_vehicle_number(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Valid vehicle number is required")
        return value.upper().strip()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.driver_image:
            data['driver_image'] = instance.driver_image.url if hasattr(instance.driver_image, 'url') else None
        return data