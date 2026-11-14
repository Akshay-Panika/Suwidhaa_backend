from rest_framework import serializers
from .models import ItServiceAd

class ItServiceAdSerializer(serializers.ModelSerializer):
    ad_image = serializers.FileField(
        required=True,
        allow_null=False,
    )
    video_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=500,
    )
    # is_home ko explicitly define karne ki zaroorat nahi hai kyunki fields="__all__" hai,
    # par aap chahein toh required=False set kar sakte hain.
    is_home = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = ItServiceAd
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["ad_image"] = (
            instance.ad_image.url
            if instance.ad_image
            else None
        )
        return data