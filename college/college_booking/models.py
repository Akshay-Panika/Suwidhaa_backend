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

    # ✅ ADDED: Room fields (optional)
    room_id = models.IntegerField(blank=True, null=True)
    room_name = models.CharField(max_length=255, blank=True, null=True)
    room_type = models.CharField(max_length=100, blank=True, null=True)
    room_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ✅ ADDED: Tiffin fields (optional)
    tiffin_id = models.IntegerField(blank=True, null=True)
    tiffin_name = models.CharField(max_length=255, blank=True, null=True)
    tiffin_type = models.CharField(max_length=100, blank=True, null=True)
    tiffin_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"College {self.college_id} booked by User {self.user_id} - {self.booking}"