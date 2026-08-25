from django.db import models
from cloudinary.models import CloudinaryField


class Student(models.Model):
    student_profile = CloudinaryField(
        "student_profile",
        folder="suwidhaa/school/student",
        blank=True,
        null=True,
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)

    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)

    father_name = models.CharField(max_length=150, blank=True, null=True)
    mother_name = models.CharField(max_length=150, blank=True, null=True)

    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    alternative_phone = models.CharField(max_length=20, blank=True, null=True)

    adhar_number = models.CharField(max_length=20, blank=True, null=True)
    SSSMID = models.CharField(max_length=50, blank=True, null=True)

    student_class = models.CharField(max_length=50, blank=True, null=True)
    student_id_card = models.CharField(max_length=50, blank=True, null=True,  unique=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)


    address = models.TextField(blank=True, null=True)
    caste_category = models.CharField(max_length=50, blank=True, null=True)

    fee_status = models.CharField(max_length=50, blank=True, null=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    check_box = models.BooleanField(default=False)
    school_type = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"