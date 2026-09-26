from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import ReportCard
from .serializers import ReportCardSerializer, ReportCardCreateSerializer


# ---------------------------------------------------------
# CREATE  ->  POST /report-cards/create/
# ---------------------------------------------------------
class ReportCardCreateView(APIView):
    def post(self, request):
        serializer = ReportCardCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'status': True,
                    'message': 'Report card created successfully',
                    'data': serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ---------------------------------------------------------
# LIST  ->  GET /report-cards/list/
# ---------------------------------------------------------
class ReportCardListView(APIView):
    def get(self, request):
        report_cards = ReportCard.objects.all().order_by('-created_at')
        serializer = ReportCardSerializer(report_cards, many=True)
        return Response(
            {
                'status': True,
                'message': 'Report cards fetched successfully',
                'count': report_cards.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# DETAIL  ->  GET / PUT / PATCH / DELETE /report-cards/list/<id>/
# ---------------------------------------------------------
class ReportCardDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(ReportCard, pk=pk)

    def get(self, request, pk):
        report_card = self.get_object(pk)
        serializer = ReportCardSerializer(report_card)
        return Response(
            {
                'status': True,
                'message': 'Report card fetched successfully',
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
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
                    'data': serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
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
                    'data': serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                'status': False,
                'message': 'Validation error',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        report_card = self.get_object(pk)
        report_card.delete()
        return Response(
            {
                'status': True,
                'message': 'Report card deleted successfully',
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# FILTER BY ADMIN ID  ->  GET /report-cards/adminid/<admin_id>/
# ---------------------------------------------------------
class ReportCardByAdminIdView(APIView):
    def get(self, request, admin_id):
        report_cards = ReportCard.objects.filter(
            admin_id=admin_id
        ).order_by('-created_at')

        if not report_cards.exists():
            return Response(
                {
                    'status': False,
                    'message': f'No report cards found for admin_id: {admin_id}',
                    'data': [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReportCardSerializer(report_cards, many=True)
        return Response(
            {
                'status': True,
                'message': f'Report cards fetched for admin_id: {admin_id}',
                'count': report_cards.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )