from rest_framework import serializers
from .models import Webseries, Season, Episode
from ott.content.models import Content


class CloudinaryInputField(serializers.Field):
    """File input → URL output"""
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


# ---------------- EPISODE ----------------
class EpisodeSerializer(serializers.ModelSerializer):
    # ✅ webseries input bhi lega, output bhi dega (model me field hai ab)
    webseries = serializers.PrimaryKeyRelatedField(
        queryset=Webseries.objects.all(), required=True
    )
    season = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(), required=True
    )

    class Meta:
        model = Episode
        # ✅ thumbnail fields removed
        fields = (
            'id',
            'webseries',        # ✅ input + output
            'season',
            'episode_number',
            'title',
            'description',
            'duration',
            'video_url',
            'release_date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        """Check: season usi webseries ka hai jo webseries me diya"""
        webseries = attrs.get('webseries')
        season = attrs.get('season')

        if season and webseries:
            if season.webseries_id != webseries.id:
                raise serializers.ValidationError({
                    "webseries": (
                        f"Season {season.season_number} (id={season.id}) "
                        f"webseries id={season.webseries_id} ka part hai, "
                        f"not webseries id={webseries.id}."
                    )
                })
        return attrs


# ---------------- SEASON (nested episodes - read only) ----------------
class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


# ---------------- WEBSERIES ----------------
class WebseriesSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Webseries
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def create(self, validated_data):
        webseries = Webseries.objects.create(**validated_data)

        Content.objects.create(
            webseries=webseries,
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

        content, _ = Content.objects.get_or_create(webseries=instance)
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