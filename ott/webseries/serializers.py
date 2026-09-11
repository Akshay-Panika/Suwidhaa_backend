from rest_framework import serializers
from .models import WebSeries, Season, Episode
from ott.content.models import Content


class CloudinaryInputField(serializers.Field):
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


# ---------- Episode ----------
class EpisodeSerializer(serializers.ModelSerializer):
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Episode
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


# ---------- Season (with nested episodes) ----------
class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = '__all__'
        read_only_fields = ('id', 'webseries', 'created_at', 'updated_at')


# ---------- WebSeries (with nested seasons) ----------
class WebSeriesSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = WebSeries
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def create(self, validated_data):
        webseries = WebSeries.objects.create(**validated_data)

        # Content auto-create (parent only)
        Content.objects.create(
            title=webseries.title,
            thumbnail_horizontal=webseries.thumbnail_horizontal.url if webseries.thumbnail_horizontal else None,
            thumbnail_vertical=webseries.thumbnail_vertical.url if webseries.thumbnail_vertical else None,
            content_type=webseries.content_type,
            release_date=webseries.release_date,
            rating=webseries.rating,
            is_trending=webseries.is_trending,
            is_recommended=webseries.is_recommended,
            is_active=webseries.is_active,
        )
        return webseries

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        content, _ = Content.objects.get_or_create(
            title=instance.title,
            content_type='webseries'
        )
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