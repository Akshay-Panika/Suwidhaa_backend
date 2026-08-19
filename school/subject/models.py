from django.db import models

# Create your models here.
from django.db import models


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    school_type = models.CharField(max_length=20, blank=True, null=True)
    asign = models.JSONField(default=list, blank=True)  # Store asignments as JSON
    check_box = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.subject_name