from django.db import models
from django.contrib.auth.hashers import make_password, check_password
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
        """Generate default password using DOB"""
        student = self.student
        if student.dob:
            dob_str = student.dob.strftime('%Y%m%d')
        else:
            from datetime import date
            dob_str = date.today().strftime('%Y%m%d')
        return dob_str
    
    def generate_student_id_card(self):
        """Generate student ID card like student-01, student-02, etc."""
        last_pass = StudentPass.objects.all().order_by('-id').first()
        if last_pass:
            # Extract number from last ID card
            try:
                last_number = int(last_pass.student_id_card.split('-')[1])
                new_number = last_number + 1
            except:
                new_number = 1
        else:
            new_number = 1
        
        return f"student-{str(new_number).zfill(2)}"
    
    def save(self, *args, **kwargs):
        if not self.student_id_card:
            self.student_id_card = self.generate_student_id_card()
        
        if not self.password:
            default_password = self.generate_default_password()
            self.set_password(default_password)
        
        super().save(*args, **kwargs)