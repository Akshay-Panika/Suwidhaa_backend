from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ott.content.models import Content
from ott.content.serializers import ContentSerializer


def _to_bool(val):
    return str(val).strip().lower() in ("true", "1", "yes", "on")


class WebseriesListAPIView(APIView):
    """
    GET /api/v1/ott/webseries/list/

    Web Series category ka saara content return karta hai.
    Content table se hi filter karke — koi alag table nahi.

    Optional boolean filters: ?is_trending=true&is_lock=true etc.
    """

    BOOL_FILTERS = [
        "is_family",
        "is_recommended",
        "is_trending",
        "is_something_new",
        "is_lock",
    ]

    def get(self, request):
        try:
            # Sirf "Web Series" category ka content
            qs = Content.objects.select_related("category").filter(
                category__name__iexact="Web Series"
            )

            # Optional boolean filters
            for field in self.BOOL_FILTERS:
                val = request.query_params.get(field)
                if val is not None and val != "":
                    qs = qs.filter(**{field: _to_bool(val)})

            serializer = ContentSerializer(qs, many=True)
            return Response(
                {
                    "success": True,
                    "count": qs.count(),   # Kitne Web Series hain
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )