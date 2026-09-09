from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    # Change from ImageField to CharField for Cloudinary URLs
    thumbnail_horizontal = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    thumbnail_vertical = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # Make other fields optional for testing
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    content_type = serializers.CharField(required=True)
    release_date = serializers.DateField(required=True)
    language = serializers.CharField(required=True)
    duration = serializers.CharField(required=True)
    video_url = serializers.URLField(required=True)
    rating = serializers.CharField(required=True)
    is_trending = serializers.BooleanField(required=False, default=False)
    is_recommended = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)

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