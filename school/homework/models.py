from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Homework(models.Model):
    # Core fields
    subject_name = models.CharField(max_length=200)
    subject_topic = models.CharField(max_length=500)
    issue_date = models.DateField(default=timezone.now)
    end_date = models.DateField()

    # Image (optional)
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


# ⬇️ NEW — multiple students per homework
class HomeworkStudent(models.Model):
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="students"
    )
    student_id = models.CharField(max_length=50)
    student_name = models.CharField(max_length=200)
    student_class = models.CharField(max_length=100, blank=True, null=True)

    # ⬇️ STATUS field (true / false)
    status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.student_name} ({self.status})"

    class Meta:
        ordering = ['id']