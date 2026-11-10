from django.db import models
from cloudinary.models import CloudinaryField

from ott.content.models import Content


class Episode(models.Model):
    """
    Episode belongs to a Web Series (Content with category 'Web Series').
    season_number is just an integer — no separate Season table.
    """

    webseries = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name="episodes",
    )

    season_number = models.PositiveIntegerField(default=1)
    episode_number = models.PositiveIntegerField()

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=False, null=False)
    duration = models.CharField(max_length=50, blank=True, null=True)

    thumbnail = CloudinaryField(
        "thumbnail",
        folder="suwidhaa/ott/webseries/episodes",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("webseries", "season_number", "episode_number")
        ordering = ["season_number", "episode_number"]
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"
        indexes = [
            models.Index(fields=["webseries", "season_number"]),
        ]

    def __str__(self):
        return f"S{self.season_number} E{self.episode_number} - {self.title}"