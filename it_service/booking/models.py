from django.db import models
from cloudinary.models import CloudinaryField

from it_service.service.models import ItServiceService


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    # ----- Relations -----
    user_id = models.IntegerField(
        db_index=True,
        help_text="User ID from main auth service",
    )
    service = models.ForeignKey(
        ItServiceService,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    # ----- Booking info -----
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    budget = models.CharField(max_length=100, blank=True, default="")
    timeline = models.CharField(max_length=100, blank=True, default="")
    message = models.TextField(blank=True, default="")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # ----- Timestamps -----
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "it_service_booking"
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["user_id", "-id"]),
            models.Index(fields=["service", "user_id"]),
        ]

    def __str__(self):
        return f"Booking {self.id} - User {self.user_id} - Service {self.service_id}"