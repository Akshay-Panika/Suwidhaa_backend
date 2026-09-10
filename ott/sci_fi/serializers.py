from rest_framework import serializers
from .models import SciFi
from ott.content.models import Content


class CloudinaryInputField(serializers.Field):
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class SciFiSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = SciFi
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def create(self, validated_data):
        sci_fi = SciFi.objects.create(**validated_data)

        Content.objects.create(
            sci_fi=sci_fi,
            title=sci_fi.title,
            thumbnail_horizontal=sci_fi.thumbnail_horizontal.url if sci_fi.thumbnail_horizontal else None,
            thumbnail_vertical=sci_fi.thumbnail_vertical.url if sci_fi.thumbnail_vertical else None,
            content_type=sci_fi.content_type,
            release_date=sci_fi.release_date,
            rating=sci_fi.rating,
            is_trending=sci_fi.is_trending,
            is_recommended=sci_fi.is_recommended,
            is_active=sci_fi.is_active,
        )
        return sci_fi

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        content, _ = Content.objects.get_or_create(sci_fi=instance)
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