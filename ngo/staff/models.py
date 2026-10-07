from django.db import models
from cloudinary.models import CloudinaryField


class NgoStaff(models.Model):
    class Role(models.TextChoices):
        MANAGER = "manager", "Manager"
        TEACHER = "teacher", "Teacher"
        VOLUNTEER = "volunteer", "Volunteer"
        COORDINATOR = "coordinator", "Coordinator"
        OTHER = "other", "Other"

    name = models.CharField(max_length=255)
    image = CloudinaryField(
        "image",
        folder="suwidhaa/ngo/staff",
        blank=False,
        null=False,
    )
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OTHER,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "NGO Staff"
        verbose_name_plural = "NGO Staff"

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"