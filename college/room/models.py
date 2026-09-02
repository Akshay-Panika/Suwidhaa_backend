from django.db import models
from cloudinary.models import CloudinaryField

class Room(models.Model):
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_booking = models.BooleanField(default=False)
    
    # Room Type
    room_type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    
    # Amenities
    wifi = models.BooleanField(default=False)
    ac = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    
    # Near College
    near_college = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - ₹{self.price}"

    class Meta:
        ordering = ['-created_at']


class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='room_images'
    )
    image = CloudinaryField(
        'image',
        folder='suwidhaa/room/images',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.room.title}"