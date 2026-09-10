from rest_framework import serializers
from .models import Sport
from ott.content.models import Content


class CloudinaryInputField(serializers.Field):
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class SportSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Sport
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def create(self, validated_data):
        sport = Sport.objects.create(**validated_data)

        Content.objects.create(
            sport=sport,
            title=sport.title,
            thumbnail_horizontal=sport.thumbnail_horizontal.url if sport.thumbnail_horizontal else None,
            thumbnail_vertical=sport.thumbnail_vertical.url if sport.thumbnail_vertical else None,
            content_type=sport.content_type,
            release_date=sport.release_date,
            rating=sport.rating,
            is_trending=sport.is_trending,
            is_recommended=sport.is_recommended,
            is_active=sport.is_active,
        )
        return sport

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        content, _ = Content.objects.get_or_create(sport=instance)
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