from django.db import models
from cloudinary.models import CloudinaryField


class Homework(models.Model):
    """
    Homework assigned by teacher to students.
    Stores student list as JSON:
      [
        {"studentIdcard": "STU001", "status": false},
        {"studentIdcard": "STU002", "status": true},
      ]
    """
    school_type = models.CharField(max_length=100, blank=True, null=True)
    class_name = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=100, blank=True, null=True)
    subject_topic = models.TextField(blank=True, null=True)

    issue_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)

    # ✅ JSON list of {studentIdcard, status}
    student_ids_list = models.JSONField(default=list, blank=True)

    # ✅ Cloudinary image field with folder
    image = CloudinaryField(
        "image",
        folder="suwidhaa/school/homework",
        blank=True,
        null=True,
    )

    teacher_id = models.CharField(max_length=50, blank=True, null=True)
    teacher_name = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "school_homework"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.class_name} - {self.subject} - {self.subject_topic}"