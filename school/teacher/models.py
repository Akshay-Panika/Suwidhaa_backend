from django.db import models
from cloudinary.models import CloudinaryField


class Teacher(models.Model):
    teacher_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    teacher_profile = CloudinaryField(
        "teacher_profile",
        folder="suwidhaa/school/teacher",
        blank=True,
        null=True,
    )
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    
    phone = models.CharField(max_length=20, blank=True, null=True)
    alt_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    
    address = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    experience = models.IntegerField(default=0, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    join_date = models.DateField(blank=True, null=True)
    
    check_box = models.BooleanField(default=False)
    subjects = models.JSONField(default=list, blank=True, null=True)
    school_type = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.teacher_id})"