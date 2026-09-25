from django.db import models
from cloudinary.models import CloudinaryField


class StudentLeave(models.Model):

    LEAVE_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    student_id_card = models.CharField(max_length=100)
    student_name = models.CharField(max_length=150)
    student_class = models.CharField(max_length=50)
    school_type = models.CharField(max_length=100)
    reason_msg = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    image = CloudinaryField(
        "student_leave",
        folder="suwidhaa/school/leave",
        blank=True,
        null=True,
    )

    # ----- New fields -----
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

    def __str__(self):
        return f"{self.student_name} - {self.student_id_card}"