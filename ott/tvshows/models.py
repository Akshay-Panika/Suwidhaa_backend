from django.db import models
from cloudinary.models import CloudinaryField

from ott.content.models import Content


class TvShowEpisode(models.Model):
    """
    Episode belongs to a TV Show (Content with category 'TV Shows').
    season_number is just an integer — no separate Season table.
    """

    tvshow = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name="tvshow_episodes",   # ✅ distinct from webseries
    )

    season_number = models.PositiveIntegerField(default=1)
    episode_number = models.PositiveIntegerField()

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=False, null=False)
    duration = models.CharField(max_length=50, blank=True, null=True)

    thumbnail = CloudinaryField(
        "thumbnail",
        folder="suwidhaa/ott/tvshows/episodes",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("tvshow", "season_number", "episode_number")
        ordering = ["season_number", "episode_number"]
        verbose_name = "TV Show Episode"
        verbose_name_plural = "TV Show Episodes"
        indexes = [
            models.Index(fields=["tvshow", "season_number"]),
        ]

    def __str__(self):
        return f"S{self.season_number} E{self.episode_number} - {self.title}"