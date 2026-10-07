from decimal import Decimal
from rest_framework import serializers

from ngo.service.models import NgoService
from .models import NgoHistory


class NgoHistorySerializer(serializers.ModelSerializer):
    # 🔽 WRITE: service_id
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=NgoService.objects.all(),
        source="service",
        write_only=True,
        required=True,
    )

    # 🔼 READ: snapshot fields
    service_name = serializers.CharField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    service_image = serializers.URLField(read_only=True)

    # 🔼 READ: live progress
    service_progress = serializers.SerializerMethodField()

    class Meta:
        model = NgoHistory
        fields = [
            "id",
            "service_id",
            "service",
            "service_name",
            "category_name",
            "service_image",
            "service_progress",
            "donor_id",
            "donor_name",
            "donor_contact",
            "donate_amount",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["service", "created_at", "updated_at"]

    def get_service_progress(self, obj):
        if not obj.service:
            return None
        return obj.service.progress or {
            "target_amount": 0,
            "total_amount": 0,
            "donor": 0,
        }

    def validate_donate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError(
                "Donate amount must be greater than zero."
            )
        return value

    def create(self, validated_data):
        """
        On create:
        - Save history
        - Bump service.progress.total_amount and service.progress.donor
        """
        instance = super().create(validated_data)

        service = instance.service
        if service:
            progress = service.progress or {}
            target = progress.get("target_amount", 0) or 0
            total = progress.get("total_amount", 0) or 0
            donor = progress.get("donor", 0) or 0

            new_total = Decimal(str(total)) + Decimal(str(instance.donate_amount))

            service.progress = {
                "target_amount": target,
                "total_amount": float(new_total),
                "donor": donor + 1,
            }
            service.save(update_fields=["progress", "updated_at"])

        return instance