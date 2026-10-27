from django.db import models

class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    is_logged_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'app_auth_user'
        ordering = ['-created_at']

    def __str__(self):
        return self.phone_number