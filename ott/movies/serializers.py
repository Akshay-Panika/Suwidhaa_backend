from rest_framework import serializers
from .models import Movie
from ott.content.models import Content


class CloudinaryInputField(serializers.Field):
    def to_representation(self, value):
        if value:
            return value.url
        return None

    def to_internal_value(self, data):
        # data = uploaded file
        return data


class MovieSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def create(self, validated_data):
        movie = Movie.objects.create(**validated_data)
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