from django.db import models
from cloudinary.models import CloudinaryField

class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['id']
    def __str__(self):
        return self.name

class Subject(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='subjects', null=True, blank=True)
    name = models.CharField(max_length=50) 
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
        unique_together = ('school_class', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.school_class.name if self.school_class else 'No Class'})"

class RecordVideo(models.Model):
    title = models.CharField(max_length=255)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='videos')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    
    thumbnail = CloudinaryField('thumbnail', folder="suwidhaa/school/record_videos", blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=False, null=False)
    duration = models.CharField(max_length=50, help_text="e.g., 5 min")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.school_class.name}"