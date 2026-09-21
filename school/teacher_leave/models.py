from django.db import models
from cloudinary.models import CloudinaryField


class TeacherLeave(models.Model):
    teacher_id = models.CharField(max_length=100)
    teacher_id_card = models.CharField(max_length=100)
    apply_status = models.BooleanField(default=True)
    reason_msg = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    image = CloudinaryField(
        "teacher_leave",
        folder="suwidhaa/school/leave",
        blank=True,
        null=True,
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teacher_leave"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.teacher_id} - {self.teacher_id_card}"