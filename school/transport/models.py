from django.db import models
from cloudinary.models import CloudinaryField
from school.school_type.models import SchoolType
from school.student.models import Student

class Transport(models.Model):
    school = models.ForeignKey(
        SchoolType,
        on_delete=models.CASCADE,
        related_name="transports",
        null=True,
        blank=True,
    )
    
    transport_type = models.CharField(max_length=100, blank=True, null=True)
    school_type = models.CharField(max_length=100, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, unique=True, db_index=True)
    
    driver_name = models.CharField(max_length=150)
    driver_number = models.CharField(max_length=20)
    driver_image = CloudinaryField(
        "driver_image",
        folder="suwidhaa/transport/drivers",
        blank=True,
        null=True
    )
    
    capacity = models.CharField(max_length=50, blank=True, null=True)
    route_name = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transport'
        verbose_name_plural = 'Transports'
    
    def __str__(self):
        return f"{self.transport_type} - {self.vehicle_number}"


class TransportStudent(models.Model):
    transport = models.ForeignKey(
        Transport,
        on_delete=models.CASCADE,
        related_name='assigned_students'
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='transport_assignments',
        null=True,
        blank=True
    )
    
    address = models.TextField(blank=True, null=True)
    pickup_time = models.CharField(max_length=50, blank=True, null=True)
    drop_time = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['student__first_name']
        verbose_name = 'Transport Student'
        verbose_name_plural = 'Transport Students'
        unique_together = [['transport', 'student']]
    
    def __str__(self):
        return f"{self.transport.vehicle_number} - {self.student.first_name if self.student else 'No Student'}"