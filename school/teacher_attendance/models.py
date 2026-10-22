# school/teacher_attendance/models.py
from django.db import models
from school.teacher.models import Teacher


class TeacherAttendance(models.Model):
    ATTENDANCE_STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    date = models.DateField(db_index=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    attendance_status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='present',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('teacher', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.teacher_id} | {self.date} | {self.attendance_status}"

    @property
    def working_hours(self):
        if self.check_in_time and self.check_out_time:
            diff = self.check_out_time - self.check_in_time
            return round(diff.total_seconds() / 3600, 2)
        return 0.0