from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from ngo.service.models import NgoService
from .models import NgoHistory
from .serializers import NgoHistorySerializer, GroupedHistorySerializer


# ═══════════════════════════════════════════════════════════════
# CREATE & LIST VIEWS
# ═══════════════════════════════════════════════════════════════
class NgoHistoryCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NgoHistorySerializer(data=request.data)
        if serializer.is_valid():
            history = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "NGO history created successfully",
                    "data": NgoHistorySerializer(history).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class NgoHistoryListView(APIView):
    def get(self, request):
        services = (
            NgoService.objects.filter(history__isnull=False)
            .distinct()
            .order_by("-id")
        )

        service_id = request.query_params.get("service_id")
        if service_id:
            services = services.filter(id=service_id)

        donor_id = request.query_params.get("donor_id")
        if donor_id:
            services = services.filter(history__donor_id=donor_id).distinct()

        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date:
            services = services.filter(history__created_at__date__gte=from_date)
        if to_date:
            services = services.filter(history__created_at__date__lte=to_date)

        serializer = GroupedHistorySerializer(services, many=True)

        return Response(
            {
                "success": True,
                "count": services.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class NgoHistoryByDonorView(APIView):
    def get(self, request, donor_id):
        qs = NgoHistory.objects.filter(donor_id=donor_id)

        agg = qs.aggregate(
            total_donated=Sum("donate_amount"),
            total_donations=Count("id"),
        )
        total_donated = float(agg["total_donated"] or 0)
        total_donations = int(agg["total_donations"] or 0)
        unique_services = qs.values("service").distinct().count()

        services = (
            NgoService.objects.filter(history__donor_id=donor_id)
            .distinct()
            .order_by("-id")
        )

        serializer = GroupedHistorySerializer(
            services, many=True, context={"donor_id": donor_id}
        )

        return Response(
            {
                "success": True,
                "donor_id": int(donor_id),
                "summary": {
                    "total_donated": total_donated,
                    "total_donations": total_donations,
                    "unique_services": unique_services,
                },
                "count": unique_services,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════════
# DONOR DELETE — poore donor ki saari history delete
# ═══════════════════════════════════════════════════════════════
class NgoHistoryByDonorDeleteView(APIView):
    """
    Ek donor_id ki saari donation history delete karta hai.
    Har affected NgoService ka progress (total_amount + donor count) adjust hoga.
    """

    def delete(self, request, donor_id):
        histories = NgoHistory.objects.filter(donor_id=donor_id)

        if not histories.exists():
            return Response(
                {
                    "success": False,
                    "message": f"No history found for donor {donor_id}",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Per-service total amount + count nikaalo
        per_service = defaultdict(lambda: {"amount": Decimal("0"), "count": 0})
        for h in histories:
            if h.service_id:
                per_service[h.service_id]["amount"] += Decimal(
                    str(h.donate_amount or 0)
                )
                per_service[h.service_id]["count"] += 1

        # Har affected service ka progress adjust karo
        for service_id, stats in per_service.items():
            try:
                service = NgoService.objects.get(pk=service_id)
            except NgoService.DoesNotExist:
                continue

            progress = service.progress or {}
            total = Decimal(str(progress.get("total_amount", 0) or 0))
            donor_cnt = int(progress.get("donor", 0) or 0)

            new_total = total - stats["amount"]
            progress["total_amount"] = float(
                new_total if new_total > 0 else Decimal("0")
            )
            progress["donor"] = max(0, donor_cnt - stats["count"])
            service.progress = progress
            service.save(update_fields=["progress", "updated_at"])

        deleted_count = histories.count()
        histories.delete()

        return Response(
            {
                "success": True,
                "message": f"All donations deleted for donor {donor_id}",
                "donor_id": donor_id,
                "deleted_count": deleted_count,
                "services_affected": len(per_service),
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════════
# DETAIL / UPDATE / DELETE  (single record)
# ═══════════════════════════════════════════════════════════════
class NgoHistoryDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return NgoHistory.objects.get(pk=pk)
        except NgoHistory.DoesNotExist:
            return None

    def get(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": NgoHistorySerializer(history).data},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = NgoHistorySerializer(history, data=request.data, partial=True)
        if serializer.is_valid():
            history = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "NGO history updated successfully",
                    "data": NgoHistorySerializer(history).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Delete hone par service progress subtract karna
    def delete(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = history.service
        if service:
            progress = service.progress or {}
            total = float(progress.get("total_amount", 0) or 0)
            donor = int(progress.get("donor", 0) or 0)

            progress["total_amount"] = max(
                0.0, total - float(history.donate_amount or 0)
            )
            progress["donor"] = max(0, donor - 1)
            service.progress = progress
            service.save(update_fields=["progress", "updated_at"])

        history.delete()
        return Response(
            {"success": True, "message": "NGO history deleted successfully"},
            status=status.HTTP_200_OK,
        )

# ═══════════════════════════════════════════════════════════════
# UPDATE AMOUNT — naya amount fill karo, progress auto-adjust
# ═══════════════════════════════════════════════════════════════
class NgoHistoryUpdateAmountView(APIView):
    """
    Donation amount ko naye value se update karta hai.
    Service progress.total_amount difference ke hisaab se auto-adjust hota hai.
    Donor count same rehta hai.
    Body: { "donate_amount": 1500 }
    """

    def post(self, request, pk):
        try:
            history = NgoHistory.objects.get(pk=pk)
        except NgoHistory.DoesNotExist:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        raw = request.data.get("donate_amount")
        if raw is None or str(raw).strip() == "":
            return Response(
                {"success": False, "message": "donate_amount is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_amount = Decimal(str(raw))
        except Exception:
            return Response(
                {"success": False, "message": "Invalid donate_amount"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_amount <= 0:
            return Response(
                {"success": False, "message": "Donate amount must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_amount = Decimal(str(history.donate_amount or 0))
        diff = new_amount - old_amount

        # Service progress adjust (only if amount changed)
        service = history.service
        if service and diff != 0:
            progress = service.progress or {}
            total = Decimal(str(progress.get("total_amount", 0) or 0))
            new_total = total + diff
            progress["total_amount"] = float(
                new_total if new_total > 0 else Decimal("0")
            )
            service.progress = progress
            service.save(update_fields=["progress", "updated_at"])

        history.donate_amount = new_amount
        history.save(update_fields=["donate_amount", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Donation amount updated successfully",
                "data": NgoHistorySerializer(history).data,
            },
            status=status.HTTP_200_OK,
        )