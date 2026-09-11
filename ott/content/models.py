# from django.db import models


# class Content(models.Model):
#     movie = models.OneToOneField(
#         'movies.Movie',
#         on_delete=models.CASCADE,   # ✅ Movie delete → Content bhi delete
#         null=True,
#         blank=True,
#         related_name='content_entry',
#     )

#     title = models.CharField(max_length=255)
#     thumbnail_horizontal = models.URLField(max_length=500, blank=True, null=True)
#     thumbnail_vertical = models.URLField(max_length=500, blank=True, null=True)
#     content_type = models.CharField(max_length=50, default='movie')
#     release_date = models.DateField()
#     rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
#     is_trending = models.BooleanField(default=False)
#     is_recommended = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} ({self.content_type})"

from django.db import models


class Content(models.Model):
    # Source references (any one will be set)
    movie = models.OneToOneField(
        'movies.Movie',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='content_entry',
    )
    cartoon = models.OneToOneField(
        'cartoons.Cartoon',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='content_entry',
    )
    sport = models.OneToOneField(
        'sports.Sport',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='content_entry',
    )
    sci_fi = models.OneToOneField(
        'sci_fi.SciFi',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='content_entry',
    )
    webseries = models.OneToOneField(
    'webseries.WebSeries',
    on_delete=models.CASCADE,
    null=True, blank=True,
    related_name='content_entry',
)
    title = models.CharField(max_length=255)
    thumbnail_horizontal = models.URLField(max_length=500, blank=True, null=True)
    thumbnail_vertical = models.URLField(max_length=500, blank=True, null=True)
    content_type = models.CharField(max_length=50, default='movie')
    release_date = models.DateField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    is_trending = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.content_type})"