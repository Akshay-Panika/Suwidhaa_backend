from rest_framework import serializers
from .models import EcommerceStore
from auth.app_auth.models import User


class EcommerceStoreSerializer(serializers.ModelSerializer):
    store_logo = serializers.FileField(
        required=True,
        allow_null=False,
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
    )

    class Meta:
        model = EcommerceStore
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_user(self, value):
        # Check if user already has a store
        if EcommerceStore.objects.filter(user=value).exists():
            raise serializers.ValidationError("This user already has a store.")
        return value

    def validate_store_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Store name cannot be empty.")
        
        # Case-insensitive duplicate check
        qs = EcommerceStore.objects.filter(store_name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This store name is already taken.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Logo URL
        data["store_logo"] = (
            instance.store_logo.url
            if instance.store_logo
            else None
        )

        # Nested user detail
        data["user_detail"] = {
            "id": instance.user.id,
            "name": instance.user.name,
            "phone_number": instance.user.phone_number,
        }

        return data