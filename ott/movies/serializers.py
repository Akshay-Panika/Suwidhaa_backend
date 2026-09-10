# from rest_framework import serializers
# from .models import Movie


# class MovieSerializer(serializers.ModelSerializer):
#     content_type = serializers.CharField(read_only=True)
#     thumbnail_horizontal = serializers.SerializerMethodField()
#     thumbnail_vertical = serializers.SerializerMethodField()

#     class Meta:
#         model = Movie
#         fields = '__all__'
#         read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

#     def get_thumbnail_horizontal(self, obj):
#         if obj.thumbnail_horizontal:
#             return obj.thumbnail_horizontal.url
#         return None

#     def get_thumbnail_vertical(self, obj):
#         if obj.thumbnail_vertical:
#             return obj.thumbnail_vertical.url
#         return None



from rest_framework import serializers
from .models import Movie
from ott.content.models import Content


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

    def create(self, validated_data):
        # 1. Movie create karo
        movie = Movie.objects.create(**validated_data)

        # 2. Content entry automatically create karo
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
        # 1. Movie update karo
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 2. Content entry bhi update karo (agar nahi hai toh create karo)
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