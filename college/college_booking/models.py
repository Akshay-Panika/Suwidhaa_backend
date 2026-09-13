# college/college_booking/models.py

from django.db import models


class CollegeBooking(models.Model):
    college_id = models.IntegerField(
        help_text="ID of the college being booked"
    )
    user_id = models.CharField(
        max_length=255,
        help_text="User ID who is booking the college"
    )
    booking = models.BooleanField(
        default=True,
        help_text="Booking status (True = booked)"
    )
    # ✅ NEW: manually diya gaya message, jo WhatsApp pe trigger hoga
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Message to send to the college on WhatsApp when booking is created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"College {self.college_id} booked by User {self.user_id} - {self.booking}"