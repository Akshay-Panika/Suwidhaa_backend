from django.db import models
from cloudinary.models import CloudinaryField
from college.category.models import CollegeCategory


class College(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact number of the college",
    )

    # ✅ NEW: FK to CollegeCategory
    category = models.ForeignKey(
        CollegeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="colleges",
        help_text="Category this college belongs to",
    )

    logo = CloudinaryField(
        "logo",
        folder="suwidhaa/college/logos",
        blank=True,
        null=True,
        help_text="College logo image",
    )
    is_recommended = models.BooleanField(
        default=False,
        help_text="Mark college as recommended (manual)",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Longitude coordinate of the college",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text="Latitude coordinate of the college",
    )
    is_booked = models.BooleanField(
        default=False,
        help_text="True if any user has booked this college",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        cat_title = self.category.title if self.category else "No Category"
        return f"{self.name} ({cat_title})"


class CollegeImage(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = CloudinaryField(
        "image",
        folder="suwidhaa/college/images",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.college.name}"