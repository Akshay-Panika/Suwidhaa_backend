# college/colleges/migrations/0009_remove_college_booking_college_is_booked_and_more.py

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0007_college_booking'),   # ✅ FIX: 0008 ki jagah 0007
    ]

    operations = [
        migrations.RemoveField(
            model_name='college',
            name='booking',
        ),
        migrations.AddField(
            model_name='college',
            name='is_booked',
            field=models.BooleanField(default=False, help_text='True if any user has booked this college'),
        ),
        migrations.AlterField(
            model_name='college',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='college',
            name='contact_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='college',
            name='is_recommended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='college',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='college',
            name='logo',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='logo'),
        ),
        migrations.AlterField(
            model_name='college',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]