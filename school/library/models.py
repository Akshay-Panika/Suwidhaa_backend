from django.db import models
from cloudinary.models import CloudinaryField


class LibraryBook(models.Model):
    author = models.CharField(max_length=150, blank=True, null=True)

    book_class = models.CharField(max_length=20)   # "6" ... "12"
    subject = models.CharField(max_length=50)      # "Maths", "Physics", ...

    quantity = models.PositiveIntegerField(default=1)

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

    # ---------- NORMALIZE ON SAVE ----------
    def save(self, *args, **kwargs):
        # Subject → "Maths", "Hindi", "English" (first letter cap, rest lower)
        if self.subject:
            self.subject = self.subject.strip().capitalize()

        # book_class → "10", "11", "12" (strip "Class " prefix if present)
        if self.book_class:
            bc = str(self.book_class).strip()
            if bc.lower().startswith("class "):
                bc = bc[6:].strip()
            self.book_class = bc

        # Author → strip
        if self.author:
            self.author = self.author.strip()

        super().save(*args, **kwargs)