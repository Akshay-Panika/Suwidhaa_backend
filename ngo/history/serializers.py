from decimal import Decimal
from rest_framework import serializers

from ngo.service.models import NgoService
from .models import NgoHistory

# ─────────────────────────────────────────────────────────────
# 1. Basic NgoHistory Serializer (Create/Detail ke liye)
# ─────────────────────────────────────────────────────────────
class NgoHistorySerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=NgoService.objects.all(),
        source="service",
        write_only=True,
        required=True,
    )
    service_name = serializers.CharField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    service_image = serializers.URLField(read_only=True)
    service_progress = serializers.SerializerMethodField()

    class Meta:
        model = NgoHistory
        fields = [
            "id", "service_id", "service", "service_name", "category_name", 
            "service_image", "service_progress", "donor_id", "donor_name", 
            "donor_contact", "donate_amount", "created_at", "updated_at",
        ]
        read_only_fields = ["service", "created_at", "updated_at"]

    def get_service_progress(self, obj):
        if not obj.service:
            return None
        return obj.service.progress or {"target_amount": 0, "total_amount": 0, "donor": 0}

    def validate_donate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Donate amount must be greater than zero.")
        return value

    def create(self, validated_data):
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


# ─────────────────────────────────────────────────────────────
# 2. Naye Grouped Serializers (Aapki requirement ke liye)
# ─────────────────────────────────────────────────────────────
class GroupedServiceInfoSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    service_image = serializers.SerializerMethodField()
    service_progress = serializers.SerializerMethodField()

    class Meta:
        model = NgoService
        fields = ['id', 'service_name', 'category_name', 'service_image', 'service_progress', 'created_at', 'updated_at']

    def get_service_image(self, obj):
        if obj.images and isinstance(obj.images, list) and len(obj.images) > 0:
            return obj.images[0]
        return None

    def get_service_progress(self, obj):
        return obj.progress or {"target_amount": 0, "total_amount": 0, "donor": 0}


class GroupedHistorySerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField()
    donor = serializers.SerializerMethodField()

    class Meta:
        model = NgoService
        fields = ['service', 'donor']

    def get_service(self, obj):
        return GroupedServiceInfoSerializer(obj).data

    def get_donor(self, obj):
        # Service ki saari history fetch karo
        histories = obj.history.all().order_by('created_at')
        
        grouped = {}
        for h in histories:
            # Unique key banane ke liye (donor_id ya contact)
            key = str(h.donor_id) if h.donor_id else f"unknown_{h.donor_contact}"
            
            if key not in grouped:
                grouped[key] = {
                    "donor_id": h.donor_id,
                    "donor_name": h.donor_name or "",
                    "donor_contact": h.donor_contact or "",
                    "donate_amount": [], # Array jisme saare amounts aayenge
                    "created_at": h.created_at,
                    "updated_at": h.updated_at,
                }
            
            # Amount list me append karo
            grouped[key]["donate_amount"].append(float(h.donate_amount))
            
            # Latest updated_at track karo
            if h.updated_at > grouped[key]["updated_at"]:
                grouped[key]["updated_at"] = h.updated_at
                
        return list(grouped.values())