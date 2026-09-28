# school/exams/models.py
from django.db import models


# ==================== CHOICES ====================
class ExamType(models.TextChoices):
    BOARD = 'board', 'Board Exam'
    HALF_YEARLY = 'halfYearly', 'Half Yearly'
    ANNUAL = 'annual', 'Annual Exam'
    PRE_BOARD = 'preBoard', 'Pre-Board'
    UNIT_TEST = 'unitTest', 'Unit Test'


# ==================== MODELS ====================
class ClassExamTimetable(models.Model):
    """
    A single exam timetable for a class + exam type + duration.
    """
    class_name = models.CharField(max_length=50, db_index=True)
    exam_type = models.CharField(
        max_length=20,
        choices=ExamType.choices,
        db_index=True,
    )
    from_date = models.DateField()
    to_date = models.DateField()

    # audit — both optional
    # 👇 CHANGED: now stores the teacher ID-card string (e.g. "St-Teacher01")
    created_by_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )
    created_by_name = models.CharField(max_length=120, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-from_date', '-created_at']
        verbose_name = 'Class Exam Timetable'
        verbose_name_plural = 'Class Exam Timetables'

    def __str__(self):
        return f"Class {self.class_name} • {self.get_exam_type_display()} ({self.from_date} → {self.to_date})"


class SubjectSchedule(models.Model):
    """
    One subject row inside a timetable.
    """
    timetable = models.ForeignKey(
        ClassExamTimetable,
        on_delete=models.CASCADE,
        related_name='schedules',
    )
    subject = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.CharField(max_length=10)
    end_time = models.CharField(max_length=10)
    invigilator = models.CharField(max_length=120)
    room = models.CharField(max_length=60)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        verbose_name = 'Subject Schedule'
        verbose_name_plural = 'Subject Schedules'

    def __str__(self):
        return f"{self.subject} • {self.date} • {self.start_time}-{self.end_time}"