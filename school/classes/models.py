from django.db import models


class Class(models.Model):
    class_name = models.CharField(max_length=50)
    school_name = models.CharField(max_length=200, blank=True, null=True)
    sections = models.JSONField(default=list, blank=True)
    check_box = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.class_name