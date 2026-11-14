from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import ItServiceService
from .serializers import ItServiceServiceSerializer


# ------------------------------------------------------------------
# HELPER
# ------------------------------------------------------------------
def get_user_bookings_map(user_id):
    """
    Return dict: { service_id: booking_info }

    Rules:
      - Cancelled bookings are IGNORED (so user can re-book)
      - If multiple active bookings exist for same service,
        the LATEST one is returned.
      - Invalid / missing user_id  ->  empty dict
    """
    if not user_id:
        return {}

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return {}

    from it_service.booking.models import Booking

    bookings = (
        Booking.objects
        .filter(user_id=user_id)
        .exclude(status="cancelled")
        .order_by("-id")           # latest first
        .values(
            "id",
            "service_id",
            "status",
            "full_name",
            "created_at",
            "updated_at",
        )
    )

    result = {}
    for b in bookings:
        sid = b["service_id"]
        if sid in result:
            continue                # keep only latest

        result[sid] = {
            "id": b["id"],
            "status": b["status"],
            "full_name": b["full_name"],
            "created_at": b["created_at"],
            "updated_at": b["updated_at"],
        }
    return result


def get_booked_service_ids(user_id):
    """
    Backward-compatible helper.
    Returns set of service IDs that have an ACTIVE booking.
    """
    return set(get_user_bookings_map(user_id).keys())


# ------------------------------------------------------------------
# BOOKED SERVICE LIST  (unchanged behaviour)
# ------------------------------------------------------------------
class BookedServiceListView(APIView):
    """
    GET /service/booked/list/?user_id=<id>
    Optional: ?status=pending|confirmed|completed|cancelled
    """
    def get(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"success": False, "message": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from it_service.booking.models import Booking

        bookings = (
            Booking.objects
            .select_related("service", "service__category")
            .filter(user_id=user_id)
            .order_by("-id")
        )

        status_filter = request.query_params.get("status")
        if status_filter:
            bookings = bookings.filter(status=status_filter)

        data = []
        for booking in bookings:
            service = booking.service
            if not service:
                continue

            item = ItServiceServiceSerializer(service).data
            item["is_booked"] = booking.status != "cancelled"
            item["booking"] = {
                "id": booking.id,
                "status": booking.status,
                "full_name": booking.full_name,
                "created_at": booking.created_at,
                "updated_at": booking.updated_at,
            }
            data.append(item)

        return Response(
            {
                "success": True,
                "count": len(data),
                "user_id": int(user_id),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# CREATE
# ------------------------------------------------------------------
class ItServiceServiceCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        serializer = ItServiceServiceSerializer(data=request.data)

        if serializer.is_valid():
            service = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service created successfully",
                    "data": ItServiceServiceSerializer(service).data,
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


# ------------------------------------------------------------------
# LIST  (🔥 UPDATED — is_booked + booking detail)
# ------------------------------------------------------------------
class ItServiceServiceListView(APIView):
    """
    GET /service/list/

    Query params:
        ?category=<id>     (0 = all categories)
        ?user_id=<id>      (optional — to get is_booked + booking detail)
    """
    def get(self, request):
        services = ItServiceService.objects.all().order_by("-id")

        # category=0 (or missing) => no filter
        category_id = request.query_params.get("category")
        if category_id and str(category_id) != "0":
            services = services.filter(category_id=category_id)

        user_id = request.query_params.get("user_id")
        bookings_map = get_user_bookings_map(user_id)

        serializer = ItServiceServiceSerializer(services, many=True)
        data = serializer.data

        for item in data:
            booking = bookings_map.get(item["id"])
            item["is_booked"] = booking is not None
            item["booking"] = booking          # None if not booked

        return Response(
            {
                "success": True,
                "count": len(data),
                "user_id": (
                    int(user_id)
                    if user_id and str(user_id).isdigit()
                    else None
                ),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# DETAIL / UPDATE / DELETE
# ------------------------------------------------------------------
class ItServiceServiceDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        try:
            return ItServiceService.objects.get(pk=pk)
        except ItServiceService.DoesNotExist:
            return None

    def get(self, request, pk):
        service = self.get_object(pk)
        if not service:
            return Response(
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_id = request.query_params.get("user_id")
        bookings_map = get_user_bookings_map(user_id)

        data = ItServiceServiceSerializer(service).data
        booking = bookings_map.get(service.id)
        data["is_booked"] = booking is not None
        data["booking"] = booking          # 🔥 consistent with list

        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        service = self.get_object(pk)
        if not service:
            return Response(
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceServiceSerializer(service, data=request.data)

        if serializer.is_valid():
            service = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service updated successfully",
                    "data": ItServiceServiceSerializer(service).data,
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
        service = self.get_object(pk)
        if not service:
            return Response(
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ItServiceServiceSerializer(
            service, data=request.data, partial=True
        )

        if serializer.is_valid():
            service = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "IT service updated successfully",
                    "data": ItServiceServiceSerializer(service).data,
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
        service = self.get_object(pk)
        if not service:
            return Response(
                {"success": False, "message": "IT service not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        service.delete()
        return Response(
            {"success": True, "message": "IT service deleted successfully"},
            status=status.HTTP_200_OK,
        )