from rest_framework import serializers
from .models import EcommerceProduct, EcommerceProductImage
from ecommerce.subcategory.models import EcommerceSubcategory
from auth.app_auth.models import User


class EcommerceProductImageSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=True, allow_null=False)

    class Meta:
        model = EcommerceProductImage
        fields = ["id", "image", "is_primary", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = instance.image.url if instance.image else None
        return data


class EcommerceProductSerializer(serializers.ModelSerializer):
    # Multiple images
    images = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        write_only=True,
        required=False,
        help_text="Multiple image files bhejo (same key 'images')",
    )

    subcategory = serializers.PrimaryKeyRelatedField(
        queryset=EcommerceSubcategory.objects.all(),
        required=True,
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True,
    )

    class Meta:
        model = EcommerceProduct
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate(self, attrs):
        price = attrs.get("price")
        old_price = attrs.get("old_price")

        if price is not None and old_price is not None:
            if old_price < price:
                raise serializers.ValidationError(
                    {"old_price": "Old price should be >= price."}
                )

        # Create pe kam se kam 1 image zaroori
        if not self.instance:
            images = attrs.get("images") or []
            if not images:
                raise serializers.ValidationError(
                    {"images": "Kam se kam 1 image required hai."}
                )

        return attrs

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        product = EcommerceProduct.objects.create(**validated_data)

        for idx, img in enumerate(images_data):
            EcommerceProductImage.objects.create(
                product=product,
                image=img,
                is_primary=(idx == 0),     # pehli image primary
                sort_order=idx,
            )

        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)

        # Basic fields update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Agar nayi images aayi hain → purani replace karo
        if images_data is not None:
            instance.images.all().delete()
            for idx, img in enumerate(images_data):
                EcommerceProductImage.objects.create(
                    product=instance,
                    image=img,
                    is_primary=(idx == 0),
                    sort_order=idx,
                )

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Nested images
        data["images"] = EcommerceProductImageSerializer(
            instance.images.all(), many=True
        ).data

        # Primary image URL (frontend convenience)
        data["primary_image"] = instance.primary_image

        # Nested details
        data["subcategory_detail"] = {
            "id": instance.subcategory.id,
            "title": instance.subcategory.title,
        }
        data["category_detail"] = {
            "id": instance.subcategory.category.id,
            "title": instance.subcategory.category.title,
        }
        data["user_detail"] = {
            "id": instance.user.id,
            "name": instance.user.name,
            "phone_number": instance.user.phone_number,
        }

        return data