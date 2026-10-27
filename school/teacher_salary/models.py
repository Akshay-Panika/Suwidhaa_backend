from django.db import models
from school.teacher.models import Teacher

class TeacherSalaryTransaction(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="salary_transactions")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.IntegerField()
    year = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-year', '-month', '-payment_date']

    def __str__(self):
        return f"{self.teacher.first_name} - {self.month}/{self.year} - {self.amount_paid}"