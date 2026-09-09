from django.db import models
from cloudinary.models import CloudinaryField


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    thumbnail_horijental = CloudinaryField(
        "thumbnail_horijental",
        folder="suwidhaa/ott/movies/horizontal",
        blank=False,
        null=False,
    )

    thumbnail_vertical = CloudinaryField(
        "thumbnail_vertical",
        folder="suwidhaa/ott/movies/vertical",
        blank=False,
        null=False,
    )

    content_type = models.CharField(max_length=50)
    release_date = models.DateField()
    language = models.CharField(max_length=100)

    duration = models.CharField(max_length=50)
    video_url = models.URLField(max_length=500)

    rating = models.CharField(max_length=20)

    is_trending = models.BooleanField()
    is_recommended = models.BooleanField()
    is_active = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title