from django.db import models
from school.school_type.models import SchoolType  # 👈 Import SchoolType

class Meeting(models.Model):
    # 🔗 Link to School
    school = models.ForeignKey(
        SchoolType, 
        on_delete=models.CASCADE, 
        related_name="meetings",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    for_meeting = models.CharField(max_length=50)   # "Student" or "Staff"
    class_name = models.CharField(max_length=100, blank=True, null=True)
    zoom_url = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        school_name = self.school.school_name if self.school else "No School"
        return f"{self.title} - {school_name} ({self.date})"