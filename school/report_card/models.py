from django.db import models


class ReportCard(models.Model):
    SCHOOL_TYPE_CHOICES = (
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('higher_secondary', 'Higher Secondary'),
        ('college', 'College'),
        ('university', 'University'),
    )

    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    )

    admin_id = models.CharField(max_length=100)
    admin_name = models.CharField(max_length=255)
    school_type = models.CharField(max_length=50, choices=SCHOOL_TYPE_CHOICES)
    class_name = models.CharField(max_length=100)
    exam_name = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=100)
    total_marks = models.IntegerField()
    student_marks = models.IntegerField()
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    remark = models.BooleanField(default=False)  # checkbox
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_card'

    def __str__(self):
        return f"{self.admin_name} - {self.subject_name} ({self.exam_name})"