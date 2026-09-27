from django.db import models
from cloudinary.models import CloudinaryField


class LibraryBook(models.Model):
    author = models.CharField(max_length=150, blank=True, null=True)

    book_class = models.CharField(max_length=20)   # "Class 6" ... "Class 12"
    subject = models.CharField(max_length=50)      # "Maths", "Physics", ...

    quantity = models.PositiveIntegerField(default=1)

    # Images (Cloudinary)
    front_image = CloudinaryField(
        "front_image",
        folder="suwidhaa/school/library",
        blank=True,
        null=True,
    )
    back_image = CloudinaryField(
        "back_image",
        folder="suwidhaa/school/library",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "school_library_book"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.book_class}) - {self.author or 'Unknown'}"

    @property
    def status(self):
        return "Available" if self.quantity > 0 else "Out of Stock"