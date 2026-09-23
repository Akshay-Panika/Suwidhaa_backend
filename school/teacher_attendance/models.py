from django.db import models
from django.conf import settings


class TeacherAttendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
        ('LEAVE', 'On Leave'),
        ('LATE', 'Late'),
        ('WEEK_OFF', 'Week Off'),   # 👈 added so backend can emit week-off too
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_logs'
    )
    date = models.DateField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('teacher', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher.username} - {self.date}"

    @property
    def working_hours(self):
        if self.check_in_time and self.check_out_time:
            diff = self.check_out_time - self.check_in_time
            return round(diff.total_seconds() / 3600, 2)
        return 0.0