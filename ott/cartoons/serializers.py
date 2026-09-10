from rest_framework import serializers
from .models import Cartoon
from ott.content.models import Content


class CloudinaryInputField(serializers.Field):
    """File input → Full URL output"""
    def to_representation(self, value):
        return value.url if value else None

    def to_internal_value(self, data):
        return data


class CartoonSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(read_only=True)
    thumbnail_horizontal = CloudinaryInputField(required=False, allow_null=True)
    thumbnail_vertical = CloudinaryInputField(required=False, allow_null=True)

    class Meta:
        model = Cartoon
        fields = '__all__'
        read_only_fields = ('id', 'content_type', 'created_at', 'updated_at')

    def create(self, validated_data):
        cartoon = Cartoon.objects.create(**validated_data)

        Content.objects.create(
            cartoon=cartoon,
            title=cartoon.title,
            thumbnail_horizontal=cartoon.thumbnail_horizontal.url if cartoon.thumbnail_horizontal else None,
            thumbnail_vertical=cartoon.thumbnail_vertical.url if cartoon.thumbnail_vertical else None,
            content_type=cartoon.content_type,
            release_date=cartoon.release_date,
            rating=cartoon.rating,
            is_trending=cartoon.is_trending,
            is_recommended=cartoon.is_recommended,
            is_active=cartoon.is_active,
        )
        return cartoon

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        content, _ = Content.objects.get_or_create(cartoon=instance)
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