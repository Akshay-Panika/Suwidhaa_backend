# school/teacher_salary/models.py
from django.db import models

from school.teacher.models import Teacher


class TeacherSalary(models.Model):
    """Monthly salary record for a teacher."""

    PAYMENT_METHODS = [
        ("Bank Transfer", "Bank Transfer"),
        ("Cash", "Cash"),
        ("Cheque", "Cheque"),
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("Online", "Online"),
    ]

    STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Processing", "Processing"),
        ("Failed", "Failed"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="salaries",
    )

    month = models.CharField(max_length=20)      # e.g. "October"
    year = models.CharField(max_length=4)        # e.g. "2026"

    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS,
        default="Cash",
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # total monthly salary
    paid_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # amount actually paid
    pending_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # auto-calculated

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )
    paid_date = models.DateField(blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]
        # Prevent duplicate salary rows for the same teacher + month + year
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "month", "year"],
                name="unique_teacher_month_year_salary",
            )
        ]

    def __str__(self):
        return f"{self.teacher} - {self.month} {self.year}"

    # ============================================================
    # AUTO CALCULATE PENDING + STATUS
    # ============================================================
    def save(self, *args, **kwargs):
        # Normalize month & year
        if self.month:
            self.month = self.month.strip().title()      # "october" -> "October"
        if self.year:
            self.year = str(self.year).strip()

        # Normalize amount types
        amount = float(self.amount or 0)
        paid = float(self.paid_amount or 0)

        # Auto-calc pending
        pending = amount - paid
        if pending < 0:
            pending = 0
        self.pending_amount = pending

        # Auto-set status
        if paid <= 0 and amount > 0:
            self.status = "Pending"
        elif paid > 0 and pending > 0:
            self.status = "Partial"
        elif amount > 0 and paid >= amount:
            self.status = "Paid"
        elif amount == 0 and paid == 0:
            self.status = "Pending"

        super().save(*args, **kwargs)