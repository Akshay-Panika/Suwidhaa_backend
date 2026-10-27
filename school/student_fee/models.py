from django.db import models
from school.student.models import Student

class StudentFeeTransaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_transactions")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"{self.student.first_name} - {self.amount_paid}"