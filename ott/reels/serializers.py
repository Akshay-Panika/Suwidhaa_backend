from rest_framework import serializers
from .models import Reel


class ReelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reel
        fields = ['id', 'title', 'youtube_url', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title empty")
        return value.strip()

    def validate_youtube_url(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("YouTube URL empty")
        if "youtube.com" not in value and "youtu.be" not in value:
            raise serializers.ValidationError("valid YouTube URL allowed")
        return value.strip()