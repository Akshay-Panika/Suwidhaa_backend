from django.db import models


class Student(models.Model):
    """
    Student master data — ek baar banega, phir update hoga.
    """
    student_card_id = models.CharField(max_length=100, unique=True, db_index=True)
    student_name = models.CharField(max_length=200)
    student_class = models.CharField(max_length=50)
    school_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student_card_id} - {self.student_name}"


class StudentAttendance(models.Model):
    """
    Daily attendance — ek student ka ek din ka record.
    (student_card_id + date) unique hai.
    """
    ATTENDANCE_STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(db_index=True)
    attendance_status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='present'
    )
    remarks = models.CharField(max_length=255, blank=True, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.student.student_card_id} | {self.date} | {self.attendance_status}"