from django.db import models
from cloudinary.models import CloudinaryField


class Notice(models.Model):
    PRIORITY_CHOICES = [
        ("Normal", "Normal"),
        ("Important", "Important"),
        ("Urgent", "Urgent"),
    ]

    AUDIENCE_CHOICES = [
        ("Students", "Students"),
        ("Parents", "Parents"),
        ("Both", "Both"),
        ("Staff", "Staff"),
    ]

    school = models.ForeignKey(
        "school_type.SchoolType",
        on_delete=models.CASCADE,
        related_name="notices",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="Normal"
    )
    audience = models.CharField(
        max_length=20, choices=AUDIENCE_CHOICES, default="Students"
    )

    assigned_class = models.CharField(max_length=100, default="All Classes")

    attachment = CloudinaryField(
        "attachment",
        folder="suwidhaa/school/notice",
        resource_type="auto",
        blank=True,
        null=True,
    )

    is_pinned = models.BooleanField(default=False)

    created_by = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.priority})"