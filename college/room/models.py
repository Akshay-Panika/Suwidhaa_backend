from django.db import models
from cloudinary.models import CloudinaryField
from college.colleges.models import College

class Room(models.Model):
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name="rooms",
    )
    room_number = models.CharField(max_length=50, default="")
    room_type = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="e.g., Single, Double, AC, Non-AC, Lab",
    )
    capacity = models.PositiveIntegerField(default=1)
    rent_or_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.college.name} - Room {self.room_number}"
    
class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = CloudinaryField(
        "image",
        folder="suwidhaa/college/rooms",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Room {self.room.room_number} ({self.room.college.name})"