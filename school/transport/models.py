# school/transport/models.py
from django.db import models
from cloudinary.models import CloudinaryField

class Transport(models.Model):
    # Transport Details (all manual entry)
    transport_type = models.CharField(max_length=100, blank=True, null=True)
    school_type = models.CharField(max_length=100, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Driver Details
    driver_name = models.CharField(max_length=150)
    driver_number = models.CharField(max_length=20)
    driver_image = CloudinaryField(
        "driver_image",
        folder="suwidhaa/transport/drivers",
        blank=True,
        null=True
    )
    
    # Students List (Manual Data Entry as JSON)
    students_data = models.JSONField(
        default=list,
        blank=True,
        help_text="List of students with their details"
    )
    
    # Additional Fields
    capacity = models.CharField(max_length=50, blank=True, null=True)
    route_name = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transport'
        verbose_name_plural = 'Transports'
    
    def __str__(self):
        return f"{self.transport_type} - {self.vehicle_number}"