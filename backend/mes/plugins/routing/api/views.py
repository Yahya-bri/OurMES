from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..application.services import TechnologyWorkflowService
from ..domain.models import (
    Technology, Operation, TechnologyOperationComponent,
    OperationProductInComponent, OperationProductOutComponent
)
from .serializers import (
    TechnologySerializer, TechnologyDetailSerializer, OperationSerializer,
    TechnologyOperationComponentSerializer, OperationProductInComponentSerializer,
    OperationProductOutComponentSerializer
)


class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'state', 'master', 'product']
    search_fields = ['number', 'name']
    ordering_fields = ['number', 'name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TechnologyDetailSerializer
        return TechnologySerializer
    
    @action(detail=True, methods=['post'])
    def change_state(self, request, pk=None):
        """Change technology state"""
        technology = self.get_object()
        new_state = request.data.get('state')
        try:
            TechnologyWorkflowService.change_state(technology, new_state)
        except ValidationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'state changed', 'new_state': technology.state})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get technology statistics"""
        return Response(TechnologyWorkflowService.stats())
    
    @action(detail=False, methods=['post'])
    def bulk_change_state(self, request):
        """Bulk change state for multiple technologies"""
        ids = request.data.get('ids', [])
        new_state = request.data.get('state')
        
        if not ids:
            return Response({'error': 'No ids provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated_count = TechnologyWorkflowService.bulk_change_state(ids, new_state)
        except ValidationError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': 'success',
            'updated_count': updated_count,
            'new_state': new_state
        })
    
    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        """Bulk activate technologies"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = TechnologyWorkflowService.bulk_activate(ids)
        return Response({'status': 'success', 'updated_count': updated_count})
    
    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        """Bulk deactivate technologies"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = TechnologyWorkflowService.bulk_deactivate(ids)
        return Response({'status': 'success', 'updated_count': updated_count})
    
    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """Bulk delete technologies"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = TechnologyWorkflowService.bulk_delete(ids)
        return Response({'status': 'success', 'deleted_count': deleted_count})
    
    @action(detail=True, methods=['post'])
    def set_master(self, request, pk=None):
        """Set this technology as master for its product"""
        technology = self.get_object()
        TechnologyWorkflowService.set_master(technology)
        return Response({'status': 'success', 'message': 'Technology set as master'})

    @action(detail=True, methods=['get'])
    def tree(self, request, pk=None):
        """Return hierarchical operation tree with timing summary."""
        technology = self.get_object()
        # Delegate to service layer for business logic
        from ..application.services import TechnologyService
        tree_data = TechnologyService.build_operation_tree(technology)
        return Response(tree_data)


class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active']
    search_fields = ['number', 'name']
    ordering_fields = ['number', 'name']


class TechnologyOperationComponentViewSet(viewsets.ModelViewSet):
    queryset = TechnologyOperationComponent.objects.all()
    serializer_class = TechnologyOperationComponentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['technology', 'operation']


class OperationProductInComponentViewSet(viewsets.ModelViewSet):
    queryset = OperationProductInComponent.objects.all()
    serializer_class = OperationProductInComponentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['operation_component', 'product']


class OperationProductOutComponentViewSet(viewsets.ModelViewSet):
    queryset = OperationProductOutComponent.objects.all()
    serializer_class = OperationProductOutComponentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['operation_component', 'product']
