from rest_framework import serializers

from .models import NgoService
from ngo.category.models import NgoCategory


class NgoServiceSerializer(serializers.ModelSerializer):
    # Accept multiple image files for upload
    images = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        write_only=False,
    )
    
    category = serializers.PrimaryKeyRelatedField(
        queryset=NgoCategory.objects.all(),
        required=True,
    )
    
    # Read-only extra fields
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = NgoService
        fields = "__all__"

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Service name cannot be empty.")

        qs = NgoService.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "A service with this name already exists."
            )

        return value

    def validate_images(self, value):
        # Allow only list of files
        if not isinstance(value, list):
            raise serializers.ValidationError("Images must be a list of files.")
        return value

    def _upload_images_to_cloudinary(self, files):
        """
        Upload each file to Cloudinary and return list of secure URLs.
        """
        import cloudinary.uploader

        urls = []
        for file in files:
            result = cloudinary.uploader.upload(
                file,
                folder="suwidhaa/ngo/service",
            )
            urls.append(result.get("secure_url"))
        return urls

    def create(self, validated_data):
        images = validated_data.pop("images", [])

        # Upload to cloudinary
        if images:
            validated_data["images"] = self._upload_images_to_cloudinary(images)
        else:
            validated_data["images"] = []

        return NgoService.objects.create(**validated_data)

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)

        if images is not None:
            # If new images provided, upload and replace
            if images:
                validated_data["images"] = self._upload_images_to_cloudinary(images)
            else:
                validated_data["images"] = []

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Ensure images is a list
        data["images"] = instance.images or []

        # Progress
        data["progress"] = instance.progress or {
            "target_amount": 0,
            "total_amount": 0,
            "donor": 0,
        }

        # Keys
        data["keys"] = instance.keys or []

        # Choose amount
        data["choose_amount"] = instance.choose_amount or []

        # Category name
        data["category_name"] = (
            instance.category.name if instance.category else None
        )

        return data