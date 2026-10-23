from django.db import models
from django.utils import timezone
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
        related_name='attendance_logs',
    )
    date = models.DateField(default=timezone.localdate)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='absent',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        unique_together = ('teacher', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher.teacher_id_card} - {self.date}"

    @property
    def working_hours(self):
        if self.check_in_time and self.check_out_time:
            diff = self.check_out_time - self.check_in_time
            return round(diff.total_seconds() / 3600, 2)
        return 0.0