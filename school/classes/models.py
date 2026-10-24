# school/classes/models.py
from django.db import models

from school.school_type.models import SchoolType
from school.teacher.models import Teacher


class Class(models.Model):
    class_name = models.CharField(max_length=50)

    school = models.ForeignKey(
        SchoolType,
        on_delete=models.CASCADE,
        related_name="classes",
        null=True,
        blank=True,
    )

    sections = models.JSONField(default=list, blank=True)
    check_box = models.BooleanField(default=False)

    class_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes_as_teacher",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        unique_together = ("class_name", "school")

    def __str__(self):
        school_name = self.school.school_name if self.school else "No school"
        return f"{self.class_name} ({school_name})"