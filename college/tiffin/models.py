from django.db import models
from cloudinary.models import CloudinaryField

class Tiffin(models.Model):
    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tiffin Type - Free text (user can enter anything)
    is_veg = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User can enter any veg type (e.g., Pure Veg, Veg, Jain Veg, etc.)"
    )
    is_nonveg = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User can enter any non-veg type (e.g., Chicken, Mutton, Fish, Egg, etc.)"
    )
    
    # Booking & Rating
    is_booking = models.BooleanField(default=False)  # True = Booked, False = Available
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        help_text="Rating out of 5"
    )
    
    # Contact Number
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact number for tiffin orders"
    )
    
    # Near College (manual entry)
    near_college = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nearby college name"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        veg_status = self.is_veg if self.is_veg else "Veg"
        nonveg_status = self.is_nonveg if self.is_nonveg else "Non-Veg"
        return f"{self.title} - ₹{self.price} ({veg_status}/{nonveg_status})"

    class Meta:
        ordering = ['-created_at']


class TiffinImage(models.Model):
    """Tiffin images with Cloudinary"""
    tiffin = models.ForeignKey(
        Tiffin,
        on_delete=models.CASCADE,
        related_name='tiffin_images'
    )
    image = CloudinaryField(
        'image',
        folder='suwidhaa/tiffin/images',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.tiffin.title}"