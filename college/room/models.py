from django.db import models
from cloudinary.models import CloudinaryField
from college.colleges.models import College


class Room(models.Model):
    user_id = models.CharField(max_length=255)

    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_booking = models.BooleanField(default=False)

    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        blank=True, null=True
    )

    room_type = models.CharField(
        max_length=255, blank=True, null=True
    )
    contact_number = models.CharField(
        max_length=20, blank=True, null=True
    )

    # Facilities will be stored as a JSON list
    # Example: ["Ac", "WiFi", "Parking"]
    facilities = models.JSONField(default=list, blank=True)

    # Old field retained for backward compatibility
    near_college = models.CharField(
        max_length=255, blank=True, null=True
    )

    college = models.ForeignKey(
        College,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rooms"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - ₹{self.price}"

    class Meta:
        ordering = ["-created_at"]


class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="room_images"
    )

    image = CloudinaryField(
        "image",
        folder="suwidhaa/room/images",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.room.title}"