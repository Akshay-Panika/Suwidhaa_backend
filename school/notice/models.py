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

    title = models.CharField(max_length=255)
    description = models.TextField()

    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="Normal"
    )
    audience = models.CharField(
        max_length=20, choices=AUDIENCE_CHOICES, default="Students"
    )

    # Class reference (string because Flutter uses names like "Class 10 - A")
    assigned_class = models.CharField(max_length=100, default="All Classes")

    # 📎 Attachment — accepts PDF, Image, or any file (Cloudinary)
    attachment = CloudinaryField(
        "attachment",
        folder="suwidhaa/school/notice",
        resource_type="auto",   # auto-detects image / video / raw (pdf, doc, etc.)
        blank=True,
        null=True,
    )

    # Options
    is_pinned = models.BooleanField(default=False)

    # Meta
    created_by = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.priority})"