from django.core.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..application.services import OrderWorkflowService
from ..domain.models import Order, OrderStateChange
from .serializers import OrderSerializer, OrderDetailSerializer, OrderStateChangeSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['state', 'active', 'product', 'company', 'production_line']
    search_fields = ['number', 'name', 'external_number']
    ordering_fields = ['number', 'created_at', 'deadline', 'date_from']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderSerializer
    
    @action(detail=True, methods=['post'])
    def change_state(self, request, pk=None):
        """Change order state and record the change"""
        order = self.get_object()
        new_state = request.data.get('state')
        worker = request.data.get('worker', '')
        try:
            change = OrderWorkflowService.change_state(order, new_state, worker)
        except ValidationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'state changed',
            'previous_state': change.source_state,
            'new_state': change.target_state
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for orders"""
        return Response(OrderWorkflowService.dashboard_stats())


class OrderStateChangeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderStateChange.objects.all()
    serializer_class = OrderStateChangeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order']
