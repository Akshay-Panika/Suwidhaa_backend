from django.db import models


class Meeting(models.Model):
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
        return f"{self.title} - {self.for_meeting} - {self.date} {self.time}"