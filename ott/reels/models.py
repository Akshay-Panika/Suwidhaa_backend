from django.db import models


class Reel(models.Model):
    title = models.CharField(max_length=255)
    youtube_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title