from django.db import models
from school.school_type.models import SchoolType
from school.teacher.models import Teacher  # 👈 Import Teacher model

class ExamType(models.TextChoices):
    BOARD = 'board', 'Board Exam'
    HALF_YEARLY = 'halfYearly', 'Half Yearly'
    ANNUAL = 'annual', 'Annual Exam'
    PRE_BOARD = 'preBoard', 'Pre-Board'
    UNIT_TEST = 'unitTest', 'Unit Test'

class ClassExamTimetable(models.Model):
    school = models.ForeignKey(
        SchoolType,
        on_delete=models.CASCADE,
        related_name="exam_timetables",
        null=True,
        blank=True
    )
    
    class_name = models.CharField(max_length=50, db_index=True)
    exam_type = models.CharField(
        max_length=20,
        choices=ExamType.choices,
        db_index=True,
    )
    from_date = models.DateField()
    to_date = models.DateField()

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

    def __str__(self):
        school_name = self.school.school_name if self.school else 'No School'
        return f"{school_name} | Class {self.class_name} • {self.get_exam_type_display()} ({self.from_date} → {self.to_date})"


class SubjectSchedule(models.Model):
    timetable = models.ForeignKey(
        ClassExamTimetable,
        on_delete=models.CASCADE,
        related_name='schedules',
    )
    subject = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.CharField(max_length=10)
    end_time = models.CharField(max_length=10)
    
    # 👇 Changed from CharField to ForeignKey
    invigilator = models.ForeignKey(
        Teacher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="invigilations"
    )
    
    room = models.CharField(max_length=60)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.subject} • {self.date} • {self.start_time}-{self.end_time}"