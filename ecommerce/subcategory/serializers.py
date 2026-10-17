from rest_framework import serializers
from .models import EcommerceSubcategory
from ecommerce.category.models import EcommerceCategory


class EcommerceSubcategorySerializer(serializers.ModelSerializer):
    image = serializers.FileField(
        required=True,
        allow_null=False,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=EcommerceCategory.objects.all(),
        required=True,
    )

    class Meta:
        model = EcommerceSubcategory
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate(self, attrs):
        # Category nikaalo (create ya update dono ke liye)
        category = attrs.get("category")
        if category is None and self.instance:
            category = self.instance.category

        title = attrs.get("title")
        if title is None and self.instance:
            title = self.instance.title

        if category and title:
            qs = EcommerceSubcategory.objects.filter(
                category=category,
                title__iexact=title.strip(),
            )
            # update ke waqt khud ko exclude karo
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    {
                        "title": "This subcategory already exists in this category."
                    }
                )

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = (
            instance.image.url
            if instance.image
            else None
        )
        # category detail bhi bhej do (optional, helpful for frontend)
        data["category_detail"] = {
            "id": instance.category.id,
            "title": instance.category.title,
        }
        return data