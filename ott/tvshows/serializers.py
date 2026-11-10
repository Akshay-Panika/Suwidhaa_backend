from rest_framework import serializers

from .models import TvShowEpisode


class CloudinaryReadField(serializers.Field):
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class TvShowEpisodeSerializer(serializers.ModelSerializer):
    thumbnail = CloudinaryReadField(required=False, allow_null=True)

    class Meta:
        model = TvShowEpisode
        fields = [
            "id",
            "tvshow",
            "season_number",
            "episode_number",
            "title",
            "description",
            "video_url",
            "duration",
            "thumbnail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "tvshow", "created_at", "updated_at")


def group_episodes_by_season(episodes):
    """
    Flat episodes list → grouped by season_number.
    Frontend ko `seasons[]` array milta hai (same as webseries).
    """
    grouped = {}
    for ep in episodes:
        grouped.setdefault(ep.season_number, []).append(ep)

    seasons = []
    for season_number in sorted(grouped.keys()):
        season_eps = sorted(grouped[season_number], key=lambda e: e.episode_number)
        seasons.append({
            "season_number": season_number,
            "episodes": TvShowEpisodeSerializer(season_eps, many=True).data,
        })
    return seasons