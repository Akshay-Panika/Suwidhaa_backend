from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "thumbnail_horizontal",
            "thumbnail_vertical",
            "content_type",
            "release_date",
            "language",
            "duration",
            "video_url",
            "rating",
            "is_trending",
            "is_recommended",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]