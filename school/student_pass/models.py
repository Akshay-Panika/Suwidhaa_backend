from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from school.student.models import Student


class StudentPass(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='student_pass'
    )
    student_id_card = models.CharField(
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
        db_table = 'student_pass'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pass for {self.student.first_name} {self.student.last_name}"
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the raw password matches the hashed password"""
        return check_password(raw_password, self.password)
    
    def generate_default_password(self):
        """Generate a default password using dob, number, and unique character"""
        student = self.student
        if student.dob:
            dob_str = student.dob.strftime('%Y%m%d')
        else:
            from datetime import date
            dob_str = date.today().strftime('%Y%m%d')
        
        unique_chars = get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        random_number = get_random_string(length=3, allowed_chars='0123456789')
        
        return f"{dob_str}{unique_chars}{random_number}"
    
    def generate_student_id_card(self):
        """Generate a unique student ID card number"""
        student = self.student
        first_part = student.first_name[:3].upper() if student.first_name else 'STU'
        last_part = student.last_name[:3].upper() if student.last_name else 'DNT'
        
        random_num = get_random_string(length=4, allowed_chars='0123456789')
        student_id = f"{first_part}{last_part}-{random_num}"
        
        while StudentPass.objects.filter(student_id_card=student_id).exists():
            random_num = get_random_string(length=4, allowed_chars='0123456789')
            student_id = f"{first_part}{last_part}-{random_num}"
        
        return student_id
    
    def save(self, *args, **kwargs):
        if not self.student_id_card:
            self.student_id_card = self.generate_student_id_card()
        
        if not self.password:
            default_password = self.generate_default_password()
            self.set_password(default_password)
        
        super().save(*args, **kwargs)