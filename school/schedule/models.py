from django.db import models

# Create your models here.
from django.db import models
from cloudinary.models import CloudinaryField


class Schedule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    school_type = models.CharField(max_length=20, blank=True, null=True)
    time = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    
    assigned_classes = models.JSONField(default=list, blank=True)
    assigned_teachers = models.JSONField(default=list, blank=True)
    event_details = models.JSONField(default=dict, blank=True, null=True)
    
    banner_image = CloudinaryField(
        "banner_image",
        folder="suwidhaa/school/schedule",
        blank=True,
        null=True,
    )
    
    pdf_file = CloudinaryField(
        "pdf_file",
        folder="suwidhaa/school/schedule",
        blank=True,
        null=True,
    )
    
    check_box = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title