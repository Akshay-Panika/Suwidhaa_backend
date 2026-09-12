from django.db import models
from cloudinary.models import CloudinaryField


class Webseries(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    thumbnail_horizontal = CloudinaryField(
        "thumbnail_horizontal",
        folder="suwidhaa/ott/webseries/horizontal",
        blank=True, null=True,
    )
    thumbnail_vertical = CloudinaryField(
        "thumbnail_vertical",
        folder="suwidhaa/ott/webseries/vertical",
        blank=True, null=True,
    )

    content_type = models.CharField(
        max_length=50,
        default='webseries',
        editable=False
    )

    release_date = models.DateField()
    language = models.CharField(max_length=100)
    duration = models.CharField(max_length=50, help_text="e.g., 2h 15m or 45m")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    is_trending = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.content_type})"


class Season(models.Model):
    webseries = models.ForeignKey(
        Webseries,
        on_delete=models.CASCADE,
        related_name='seasons'
    )
    season_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('webseries', 'season_number')
        ordering = ['season_number']

    def __str__(self):
        return f"{self.webseries.title} - S{self.season_number}"


class Episode(models.Model):
    # ✅ webseries direct parent
    webseries = models.ForeignKey(
        Webseries,
        on_delete=models.CASCADE,
        related_name='episodes',
        null=True, blank=True,   # existing rows ke liye (migration friendly)
    )
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,
        related_name='episodes'
    )
    episode_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    thumbnail_horizontal = CloudinaryField(
        "episode_thumbnail_horizontal",
        folder="suwidhaa/ott/webseries/episodes/horizontal",
        blank=True, null=True,
    )
    thumbnail_vertical = CloudinaryField(
        "episode_thumbnail_vertical",
        folder="suwidhaa/ott/webseries/episodes/vertical",
        blank=True, null=True,
    )

    duration = models.CharField(max_length=50, help_text="e.g., 45m")
    video_url = models.URLField(max_length=500)
    release_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('season', 'episode_number')
        ordering = ['episode_number']

    def __str__(self):
        return f"{self.season} - Ep {self.episode_number}: {self.title}"