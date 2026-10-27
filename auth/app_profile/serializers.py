from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["profile_image"] = (
            instance.profile_image.url if instance.profile_image else None
        )
        return data