from rest_framework import serializers
from .models import College, CollegeImage
from college.category.models import CollegeCategory


# ── Nested Category Serializer ────────────────
class CollegeCategoryNestedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = CollegeCategory
        fields = ["id", "title", "image", "created_at", "updated_at"]

    def get_image(self, obj):
        return obj.image.url if obj.image else None


class CollegeImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = CollegeImage
        fields = ["id", "url", "created_at"]

    def get_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CollegeSerializer(serializers.ModelSerializer):
    # ✅ Nested category response
    category = CollegeCategoryNestedSerializer(read_only=True)

    # ✅ Write-only field for input
    category_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    images = CollegeImageSerializer(many=True, read_only=True)
    logo_url = serializers.SerializerMethodField()
    booking = serializers.SerializerMethodField()

    class Meta:
        model = College
        fields = [
            "id",
            "name",
            "address",
            "website",
            "contact_number",
            "category",        # nested read
            "category_id",     # write input
            "logo_url",
            "is_recommended",
            "longitude",
            "latitude",
            "booking",
            "images",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None

    def get_booking(self, obj):
        user_id = self.context.get("user_id")
        if user_id:
            from college.college_booking.models import CollegeBooking

            return CollegeBooking.objects.filter(
                college_id=obj.id,
                user_id=str(user_id),
                booking=True,
            ).exists()
        return False

    # ── Validate category_id exists ──────────
    def validate_category_id(self, value):
        if value is None:
            return value
        if not CollegeCategory.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                "Invalid category_id — category does not exist."
            )
        return value