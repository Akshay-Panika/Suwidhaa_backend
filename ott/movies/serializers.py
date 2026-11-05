from rest_framework import serializers
from .models import Movie

# ✅ Cross-app import — MovieSerializer needs Category for validation
from ott.category.models import Category   # adjust to your app path
from ott.content.models import Content     # existing


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output"""

    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class MovieSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    # Read-only helper — Flutter gets label without extra call
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "category",           # writable FK (send real category id)
            "category_name",      # read-only label
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
        read_only_fields = ("id", "content_type", "created_at", "updated_at")
        extra_kwargs = {
            "category": {"required": True, "allow_null": False},
        }

    # ---------- validation ----------
    def validate_category(self, value):
        if value is None:
            raise serializers.ValidationError(
                'Category is required. "All Content" (id=0) is virtual — pick a real category.'
            )
        return value

    # ---------- create ----------
    def create(self, validated_data):
        movie = Movie.objects.create(**validated_data)

        # Auto-sync into Content table so OTT feed picks it up
        Content.objects.create(
            movie=movie,
            title=movie.title,
            thumbnail_horizontal=movie.thumbnail_horizontal.url if movie.thumbnail_horizontal else None,
            thumbnail_vertical=movie.thumbnail_vertical.url if movie.thumbnail_vertical else None,
            content_type=movie.content_type,
            release_date=movie.release_date,
            rating=movie.rating,
            is_trending=movie.is_trending,
            is_recommended=movie.is_recommended,
            is_active=movie.is_active,
        )
        return movie

    # ---------- update ----------
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        content, _ = Content.objects.get_or_create(movie=instance)
        content.title = instance.title
        content.thumbnail_horizontal = instance.thumbnail_horizontal.url if instance.thumbnail_horizontal else None
        content.thumbnail_vertical = instance.thumbnail_vertical.url if instance.thumbnail_vertical else None
        content.content_type = instance.content_type
        content.release_date = instance.release_date
        content.rating = instance.rating
        content.is_trending = instance.is_trending
        content.is_recommended = instance.is_recommended
        content.is_active = instance.is_active
        content.save()

        return instance