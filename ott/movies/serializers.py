from rest_framework import serializers
from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = serializers.SerializerMethodField()
    thumbnail_vertical = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def get_thumbnail_horizontal(self, obj):
        if obj.thumbnail_horizontal:
            return obj.thumbnail_horizontal.url
        return None

    def get_thumbnail_vertical(self, obj):
        if obj.thumbnail_vertical:
            return obj.thumbnail_vertical.url
        return None