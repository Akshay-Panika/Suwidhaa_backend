from django.db import models

from school.teacher.models import Teacher


class TeacherSalary(models.Model):
    """Monthly salary record for a teacher."""

    PAYMENT_METHODS = [
        ("Bank Transfer", "Bank Transfer"),
        ("Cash", "Cash"),
        ("Cheque", "Cheque"),
        ("UPI", "UPI"),
    ]

    STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Failed", "Failed"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="salaries",
    )

    month = models.CharField(max_length=20)          # e.g. "October"
    year = models.CharField(max_length=4)            # e.g. "2025"

    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS,
        default="Bank Transfer",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)         # total salary
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)    # amount paid
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # amount pending

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    paid_date = models.DateField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.teacher} - {self.month} {self.year}"

    def save(self, *args, **kwargs):
        # ==== NORMALIZE MONTH & YEAR ====
        if self.month:
            self.month = self.month.strip().title()   # "october" -> "October"
        if self.year:
            self.year = str(self.year).strip()

        # ==== AUTO CALCULATE PENDING AMOUNT ====
        self.pending_amount = (self.amount or 0) - (self.paid_amount or 0)
        if self.pending_amount < 0:
            self.pending_amount = 0

        # ==== AUTO SET STATUS ====
        if self.paid_amount and self.amount and self.paid_amount >= self.amount:
            self.status = "Paid"
        else:
            self.status = "Pending"

        super().save(*args, **kwargs)