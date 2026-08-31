from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Homework(models.Model):
    subject_name = models.CharField(max_length=200)
    subject_topic = models.CharField(max_length=500)
    issue_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    image = CloudinaryField(
        "homework_image",
        folder="suwidhaa/school/homework",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_name} - {self.subject_topic}"

    class Meta:
        ordering = ['-issue_date']