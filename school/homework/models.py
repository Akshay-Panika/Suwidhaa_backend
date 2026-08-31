from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Homework(models.Model):
    # Core fields
    subject_name = models.CharField(max_length=200)
    subject_topic = models.CharField(max_length=500)
    issue_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    
    # Image field (optional)
    image = CloudinaryField(
        "homework_image",
        folder="suwidhaa/school/homework",
        blank=True,
        null=True
    )
    
    # Additional fields
    class_name = models.CharField(max_length=100, blank=True, null=True)
    teacher_name = models.CharField(max_length=200, blank=True, null=True)
    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    school_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_name} - {self.subject_topic}"

    class Meta:
        ordering = ['-issue_date']