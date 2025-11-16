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
        """Return hierarchical operation tree with input/output products and timing summary.
        The tree is ordered by node_number lexical order. Each node includes:
        - operation basic data
        - parent node_number
        - input_products / output_products lists
        - effective timing (fallback to operation if override not set)
        A root level summary aggregates total tj, tpz and time_next_operation.
        """
        technology = self.get_object()
        components = technology.operation_components.select_related('operation', 'parent').prefetch_related(
            'input_products__product', 'output_products__product', 'operation__workstations'
        ).order_by('node_number')

        def effective_val(component, field):
            override = getattr(component, field)
            if override is not None:
                return override
            return getattr(component.operation, field)

        tree_nodes = []
        total_tj = 0
        total_tpz = 0
        total_next = 0
        for comp in components:
            tj = effective_val(comp, 'tj') or 0
            tpz = effective_val(comp, 'tpz') or 0
            tnext = effective_val(comp, 'time_next_operation') or 0
            total_tj += tj
            total_tpz += tpz
            total_next += tnext
            tree_nodes.append({
                'node_number': comp.node_number,
                'parent_node_number': comp.parent.node_number if comp.parent else None,
                'priority': comp.priority,
                'operation': {
                    'number': comp.operation.number,
                    'name': comp.operation.name,
                    'workstations': [w.number for w in comp.operation.workstations.all()],
                    'tj': tj,
                    'tpz': tpz,
                    'time_next_operation': tnext,
                },
                'input_products': [
                    {
                        'number': ip.product.number,
                        'name': ip.product.name,
                        'quantity': str(ip.quantity)
                    } for ip in comp.input_products.all()
                ],
                'output_products': [
                    {
                        'number': op.product.number,
                        'name': op.product.name,
                        'quantity': str(op.quantity)
                    } for op in comp.output_products.all()
                ]
            })

        return Response({
            'technology': {
                'number': technology.number,
                'name': technology.name,
                'product': technology.product.number if technology.product_id else None,
                'state': technology.state,
            },
            'summary': {
                'total_tj': total_tj,
                'total_tpz': total_tpz,
                'total_time_next_operation': total_next,
                'nodes': len(tree_nodes)
            },
            'tree': tree_nodes
        })


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
