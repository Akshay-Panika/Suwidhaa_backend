from django.db import models
from cloudinary.models import CloudinaryField

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

    month = models.CharField(max_length=20)          # e.g. "September"
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
        unique_together = ("teacher", "month", "year")

    def __str__(self):
        return f"{self.teacher} - {self.month} {self.year}"

    def save(self, *args, **kwargs):
        # auto calculate pending
        self.pending_amount = (self.amount or 0) - (self.paid_amount or 0)
        if self.pending_amount < 0:
            self.pending_amount = 0
        super().save(*args, **kwargs)


class TeacherExtraSalary(models.Model):
    """Extra salary earned by teacher (extra classes, duty, events)."""

    STATUS_CHOICES = [
        ("Approved", "Approved"),
        ("Paid", "Paid"),
        ("Rejected", "Rejected"),
    ]

    TYPE_CHOICES = [
        ("Teaching", "Teaching"),
        ("Duty", "Duty"),
        ("Event", "Event"),
        ("Meeting", "Meeting"),
        ("Other", "Other"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="extra_salaries",
    )

    title = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="Teaching")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Approved")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.teacher} - {self.title}"


class TeacherSalaryRequest(models.Model):
    """Teacher-submitted request for extra salary."""

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="salary_requests",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.teacher} - {self.title} ({self.status})"


class TeacherPendingSalary(models.Model):
    """Pending salary entry — useful for tracking overdue payments."""

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="pending_salaries",
    )

    month = models.CharField(max_length=50)          # e.g. "October 2025"
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    due_date = models.DateField(blank=True, null=True)
    days_late = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.teacher} - {self.month}"


class TeacherBankDetail(models.Model):
    """Bank details for a teacher (used for salary transfer)."""

    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,
        related_name="bank_detail",
    )

    bank_name = models.CharField(max_length=150, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=30, blank=True, null=True)
    branch = models.CharField(max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.teacher} - {self.bank_name}"