from rest_framework import serializers
from .models import EcommerceStore
from auth.app_auth.models import User
from ecommerce.category.models import EcommerceCategory  # <-- Import


class EcommerceStoreSerializer(serializers.ModelSerializer):
    store_logo = serializers.FileField(
        required=False, 
        allow_null=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
    )
    
    # Category ID pass karne ke liye
    store_category = serializers.PrimaryKeyRelatedField(
        queryset=EcommerceCategory.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = EcommerceStore
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_user(self, value):
        qs = EcommerceStore.objects.filter(user=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This user already has a store.")
        return value

    def validate_store_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Store name cannot be empty.")
        
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

        # Category Detail (Jab ID dalenge to ye data aayega)
        if instance.store_category:
            data["store_category_detail"] = {
                "id": instance.store_category.id,
                "title": instance.store_category.title,
                "image": instance.store_category.image.url if instance.store_category.image else None
            }
        else:
            data["store_category_detail"] = None

        # User Detail
        data["user_detail"] = {
            "id": instance.user.id,
            "name": instance.user.name,
            "phone_number": instance.user.phone_number,
        }

        return data