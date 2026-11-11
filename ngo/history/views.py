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
# CREATE & LIST VIEWS (Same as before)
# ═══════════════════════════════════════════════════════════════
class NgoHistoryCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = NgoHistorySerializer(data=request.data)
        if serializer.is_valid():
            history = serializer.save()
            return Response(
                {"success": True, "message": "NGO history created successfully", "data": NgoHistorySerializer(history).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "message": "Validation failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

class NgoHistoryListView(APIView):
    def get(self, request):
        services = NgoService.objects.filter(history__isnull=False).distinct().order_by("-id")

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
            {"success": True, "count": services.count(), "data": serializer.data},
            status=status.HTTP_200_OK,
        )

class NgoHistoryByDonorView(APIView):
    def get(self, request, donor_id):
        qs = NgoHistory.objects.filter(donor_id=donor_id)
        
        agg = qs.aggregate(total_donated=Sum("donate_amount"), total_donations=Count("id"))
        total_donated = float(agg["total_donated"] or 0)
        total_donations = int(agg["total_donations"] or 0)
        unique_services = qs.values("service").distinct().count()

        services = NgoService.objects.filter(
            history__donor_id=donor_id
        ).distinct().order_by("-id")

        serializer = GroupedHistorySerializer(
            services, many=True, context={'donor_id': donor_id}
        )

        return Response(
            {
                "success": True,
                "donor_id": int(donor_id),
                "summary": {
                    "total_donated": total_donated,
                    "total_donations": total_donations,
                    "unique_services": unique_services
                },
                "count": unique_services,
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
            return Response({"success": False, "message": "NGO history not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": NgoHistorySerializer(history).data}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response({"success": False, "message": "NGO history not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = NgoHistorySerializer(history, data=request.data, partial=True)
        if serializer.is_valid():
            history = serializer.save()
            return Response({"success": True, "message": "NGO history updated successfully", "data": NgoHistorySerializer(history).data}, status=status.HTTP_200_OK)
        return Response({"success": False, "message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # 👇 NEW: Delete hone par service progress subtract karna
    def delete(self, request, pk):
        history = self.get_object(pk)
        if not history:
            return Response({"success": False, "message": "NGO history not found"}, status=status.HTTP_404_NOT_FOUND)
        
        service = history.service
        if service:
            progress = service.progress or {}
            total = float(progress.get("total_amount", 0))
            donor = int(progress.get("donor", 0))
            
            progress["total_amount"] = max(0.0, total - float(history.donate_amount))
            progress["donor"] = max(0, donor - 1)
            service.progress = progress
            service.save(update_fields=["progress", "updated_at"])

        history.delete()
        return Response({"success": True, "message": "NGO history deleted successfully"}, status=status.HTTP_200_OK)