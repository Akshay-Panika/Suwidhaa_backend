from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')