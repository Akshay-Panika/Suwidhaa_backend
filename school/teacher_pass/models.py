from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from school.teacher.models import Teacher


class TeacherPass(models.Model):
    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,
        related_name='teacher_pass'
    )
    teacher_id_card = models.CharField(
        max_length=50,
        unique=True,
        db_index=True
    )
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teacher_pass'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pass for {self.teacher.first_name} {self.teacher.last_name}"
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def generate_default_password(self):
        from datetime import date
        return self.teacher.dob.strftime('%Y%m%d') if self.teacher.dob else date.today().strftime('%Y%m%d')
    
    def save(self, *args, **kwargs):
        if not self.password:
            self.set_password(self.generate_default_password())
        super().save(*args, **kwargs)