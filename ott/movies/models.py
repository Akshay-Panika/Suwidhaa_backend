from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    thumbnail_horijental = models.URLField(max_length=500, blank=True, null=True)
    thumbnail_vertical = models.URLField(max_length=500, blank=True, null=True)

    content_type = models.CharField(max_length=50, default="movie")
    release_date = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)

    duration = models.CharField(max_length=50, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)

    age_rating = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title