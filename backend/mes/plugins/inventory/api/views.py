from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..domain.models import MaterialStock, Container, TraceabilityRecord, KanbanCard
from .serializers import MaterialStockSerializer, ContainerSerializer, TraceabilityRecordSerializer, KanbanCardSerializer
from django.utils import timezone


class MaterialStockViewSet(viewsets.ModelViewSet):
    queryset = MaterialStock.objects.all()
    serializer_class = MaterialStockSerializer
    filterset_fields = ['location_type', 'material']


class ContainerViewSet(viewsets.ModelViewSet):
    queryset = Container.objects.all()
    serializer_class = ContainerSerializer


class TraceabilityRecordViewSet(viewsets.ModelViewSet):
    queryset = TraceabilityRecord.objects.all()
    serializer_class = TraceabilityRecordSerializer
    filterset_fields = ['finished_good_batch', 'raw_material_batch']


class KanbanCardViewSet(viewsets.ModelViewSet):
    queryset = KanbanCard.objects.all()
    serializer_class = KanbanCardSerializer

    @action(detail=True, methods=['post'])
    def trigger_replenishment(self, request, pk=None):
        card = self.get_object()
        card.status = 'replenishing'
        card.save()
        return Response({'status': 'replenishing'})

    @action(detail=True, methods=['post'])
    def complete_replenishment(self, request, pk=None):
        card = self.get_object()
        card.status = 'full'
        card.last_replenished = timezone.now()
        card.save()
        return Response({'status': 'full'})
