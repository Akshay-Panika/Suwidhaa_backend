from django.db import models
from cloudinary.models import CloudinaryField

class SchoolClass(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., Nursery, Class 1
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g., Rhymes, ABC, Numbers
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class RecordVideo(models.Model):
    title = models.CharField(max_length=255)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='videos')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='videos')
    
    thumbnail = CloudinaryField('thumbnail', folder="suwidhaa/school/record_videos", blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=False, null=False)
    
    duration = models.CharField(max_length=50, help_text="e.g., 5 min")
    age_group = models.CharField(max_length=50, help_text="e.g., 3+", blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.school_class.name}"