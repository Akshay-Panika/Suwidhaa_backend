from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import ReportCard
from .serializers import ReportCardSerializer, ReportCardCreateSerializer


class ReportCardListCreateView(APIView):
    """
    GET  -> List all report cards
    POST -> Create a new report card
    """

    def get(self, request):
        report_cards = ReportCard.objects.all().order_by('-created_at')
        serializer = ReportCardSerializer(report_cards, many=True)
        return Response(
            {
                'status': True,
                'message': 'Report cards fetched successfully',
                'count': report_cards.count(),
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ReportCardCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card created successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ReportCardDetailView(APIView):
    """
    GET    -> Retrieve a single report card
    PUT    -> Update a report card
    PATCH  -> Partial update
    DELETE -> Delete a report card
    """

    def get_object(self, pk):
        return get_object_or_404(ReportCard, pk=pk)

    def get(self, request, pk):
        report_card = self.get_object(pk)
        serializer = ReportCardSerializer(report_card)
        return Response(
            {
                'status': True,
                'message': 'Report card fetched successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        report_card = self.get_object(pk)
        serializer = ReportCardCreateSerializer(report_card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        report_card = self.get_object(pk)
        serializer = ReportCardCreateSerializer(
            report_card, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card partially updated successfully',
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        report_card = self.get_object(pk)
        report_card.delete()
        return Response(
            {
                'status': True,
                'message': 'Report card deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )