from decimal import Decimal

from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import NgoHistory
from .serializers import NgoHistorySerializer


# ═══════════════════════════════════════════════════════════════
# CREATE
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


# ═══════════════════════════════════════════════════════════════
# LIST (with filters: service_id, donor_id, from, to)
# ═══════════════════════════════════════════════════════════════
class NgoHistoryListView(APIView):

    def get(self, request):
        qs = NgoHistory.objects.all().order_by("-id")

        # 🔎 Filters
        service_id = request.query_params.get("service_id")
        if service_id:
            qs = qs.filter(service_id=service_id)

        donor_id = request.query_params.get("donor_id")
        if donor_id:
            qs = qs.filter(donor_id=donor_id)

        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)

        serializer = NgoHistorySerializer(qs, many=True)

        return Response(
            {
                "success": True,
                "count": qs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════════
# DONOR-WISE LIST  →  /history/donor/<donor_id>/
# ═══════════════════════════════════════════════════════════════
class NgoHistoryByDonorView(APIView):
    """
    Returns all donations for a specific donor + summary totals.
    """

    def get(self, request, donor_id):
        qs = NgoHistory.objects.filter(donor_id=donor_id).order_by("-id")

        # Optional date filters
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)

        serializer = NgoHistorySerializer(qs, many=True)

        # 📊 Aggregates
        agg = qs.aggregate(
            total_donated=Sum("donate_amount"),
            total_donations=Count("id"),
        )

        total_donated = float(agg["total_donated"] or 0)
        total_donations = int(agg["total_donations"] or 0)

        # Unique services donated to
        unique_services = qs.values("service").distinct().count()

        return Response(
            {
                "success": True,
                "donor_id": int(donor_id),
                "summary": {
                    "total_donated": total_donated,
                    "total_donations": total_donations,
                    "unique_services": unique_services,
                },
                "count": total_donations,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ═══════════════════════════════════════════════════════════════
# DETAIL / UPDATE / DELETE
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
            {
                "success": True,
                "data": NgoHistorySerializer(history).data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NgoHistorySerializer(history, data=request.data)
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

    def patch(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NgoHistorySerializer(
            history, data=request.data, partial=True
        )
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

    def delete(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response(
                {"success": False, "message": "NGO history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        history.delete()
        return Response(
            {
                "success": True,
                "message": "NGO history deleted successfully",
            },
            status=status.HTTP_200_OK,
        )