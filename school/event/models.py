from django.db import models
from cloudinary.models import CloudinaryField
from school.school_type.models import SchoolType

class SchoolEvent(models.Model):
    CATEGORY_CHOICES = [
        ("Sports", "Sports"),
        ("Cultural", "Cultural"),
        ("Academic", "Academic"),
        ("Holiday", "Holiday"),
        ("Meeting", "Meeting"),
        ("Other", "Other"),
    ]

    AUDIENCE_CHOICES = [
        ("Students", "Students"),
        ("Parents", "Parents"),
        ("Both", "Both"),
        ("Staff", "Staff"),
        ("All", "All"),
    ]

    STATUS_CHOICES = [
        ("Upcoming", "Upcoming"),
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    # 🔗 Link to School
    school = models.ForeignKey(
        SchoolType, 
        on_delete=models.CASCADE, 
        related_name="events",
        null=True,    # <--- MUST BE HERE
        blank=True    # <--- MUST BE HERE
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="Sports"
    )
    venue = models.CharField(max_length=200)

    # Dates & Times
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50)
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)

    organizer = models.CharField(max_length=150, blank=True, null=True)
    audience = models.CharField(
        max_length=20, choices=AUDIENCE_CHOICES, default="Both"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Upcoming"
    )

    # 📸 Banner image (Cloudinary)
    banner = CloudinaryField(
        "banner",
        folder="suwidhaa/school/event",
        resource_type="image",
        blank=True,
        null=True,
    )

    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.school.school_name})"