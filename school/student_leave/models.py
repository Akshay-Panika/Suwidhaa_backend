from django.db import models
from cloudinary.models import CloudinaryField
from school.school_type.models import SchoolType


class StudentLeave(models.Model):

    LEAVE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    student_id_card = models.CharField(max_length=100)
    student_name = models.CharField(max_length=150)
    student_class = models.CharField(max_length=50)

    # Keep for backward compatibility (school name / type as string)
    school_type = models.CharField(max_length=100, blank=True, null=True)

    # ✅ NEW: proper FK so we can filter by school id
    school = models.ForeignKey(
        SchoolType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_leaves",
    )

    reason_msg = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    image = CloudinaryField(
        "student_leave",
        folder="suwidhaa/school/leave",
        blank=True,
        null=True,
    )

    # ----- Approval fields -----
    leave_status = models.CharField(
        max_length=20,
        choices=LEAVE_STATUS_CHOICES,
        default="pending",
    )
    teacher_card_id = models.CharField(max_length=100, blank=True, null=True)
    teacher_name = models.CharField(max_length=150, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_leave"
        ordering = ["-created_date"]
        indexes = [
            models.Index(fields=["school", "student_class"]),
            models.Index(fields=["student_id_card"]),
        ]

    def __str__(self):
        return f"{self.student_name} - {self.student_id_card}"