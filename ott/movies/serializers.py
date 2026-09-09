from rest_framework import serializers

from .models import Movie


class MovieSerializer(serializers.ModelSerializer):

    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    thumbnail_horijental = serializers.ImageField(required=True)
    thumbnail_vertical = serializers.ImageField(required=True)

    content_type = serializers.CharField(required=True)
    release_date = serializers.DateField(required=True)
    language = serializers.CharField(required=True)
    duration = serializers.CharField(required=True)
    video_url = serializers.URLField(required=True)
    rating = serializers.CharField(required=True)
    is_trending = serializers.BooleanField(required=True)
    is_recommended = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)

    class Meta:
        model = Movie

        fields = [
            "id",
            "title",
            "description",
            "thumbnail_horijental",
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

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]