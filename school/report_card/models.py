from django.db import models


class ReportCard(models.Model):
    RESULT_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
    )

    # ✅ Renamed from admin_id → teacher_id (stores teacher_id_card)
    teacher_id = models.CharField(max_length=100, db_index=True)

    # ✅ Stores Student DB integer id (as string). NOT id_card.
    student_id = models.CharField(max_length=100, db_index=True)

    class_name = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=100)
    exam_name = models.CharField(max_length=100)

    sujectmaks_marks = models.IntegerField()   # total marks
    pasingmaks_marks = models.IntegerField()   # passing marks
    student_marks = models.IntegerField()

    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'report_card'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.teacher_id} - {self.subject_name} ({self.exam_name})"