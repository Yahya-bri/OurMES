from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from ..domain.models import Scheduling
from .serializers import SchedulingSerializer, BulkSchedulingUpdateSerializer
from mes.plugins.orders.domain.models import Order
from mes.plugins.routing.domain.models import TechnologyOperationComponent


class SchedulingViewSet(viewsets.ModelViewSet):
    queryset = Scheduling.objects.select_related(
        'order',
        'order__product',
        'component',
        'component__operation'
    ).prefetch_related('component__operation__workstations')
    serializer_class = SchedulingSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by order(s)
        order_id = self.request.query_params.get('order')
        order_ids = self.request.query_params.get('order__in')
        workstation_id = self.request.query_params.get('workstation')
        
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        elif order_ids:
            order_id_list = [int(id.strip()) for id in order_ids.split(',') if id.strip()]
            queryset = queryset.filter(order_id__in=order_id_list)

        if workstation_id and str(workstation_id).isdigit():
            queryset = queryset.filter(component__operation__workstations__id=int(workstation_id))
        
        return queryset.order_by('order', 'sequence_index')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a naive forward schedule for an order's technology components.
        Body: {"order": <order_id>, "start": "ISO datetime"}
        Algorithm: lexical order of node_number, accumulate tj+tpz+time_next_operation.
        """
        order_id = request.data.get('order')
        start_raw = request.data.get('start')
        if not order_id:
            return Response({'error': 'order required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.select_related('technology').get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'order not found'}, status=status.HTTP_404_NOT_FOUND)
        if not order.technology_id:
            return Response({'error': 'order has no technology'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            start = timezone.datetime.fromisoformat(start_raw) if start_raw else timezone.now()
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
        except Exception:
            start = timezone.now()
        components = order.technology.operation_components.select_related('operation').order_by('node_number')
        created = []
        cursor = start
        for idx, comp in enumerate(components):
            tj = comp.tj if comp.tj is not None else comp.operation.tj
            tpz = comp.tpz if comp.tpz is not None else comp.operation.tpz
            tnext = comp.time_next_operation if comp.time_next_operation is not None else comp.operation.time_next_operation
            duration = tj + tpz
            end = cursor + timedelta(seconds=duration)
            item = Scheduling.objects.create(
                order=order,
                component=comp,
                sequence_index=idx,
                planned_start=cursor,
                planned_end=end,
                duration_seconds=duration,
                buffer_seconds=tnext,
                description=f"Auto generated for {comp.operation.number}"
            )
            created.append(item)
            cursor = end + timedelta(seconds=tnext)
        ser = SchedulingSerializer(created, many=True)
        return Response({'items': ser.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def generate_multi(self, request):
        """Generate schedules for multiple orders sequentially or in parallel.
        Body: {"orders": [<order_id>, ...], "start": "ISO datetime", "parallel": false}
        """
        order_ids = request.data.get('orders', [])
        start_raw = request.data.get('start')
        parallel = request.data.get('parallel', False)
        
        if not order_ids:
            return Response({'error': 'orders list required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start = timezone.datetime.fromisoformat(start_raw) if start_raw else timezone.now()
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
        except Exception:
            start = timezone.now()
        
        all_created = []
        cursor = start
        
        with transaction.atomic():
            for order_id in order_ids:
                try:
                    order = Order.objects.select_related('technology').get(pk=order_id)
                    if not order.technology_id:
                        continue
                    
                    components = order.technology.operation_components.select_related('operation').order_by('node_number')
                    order_cursor = start if parallel else cursor
                    
                    for idx, comp in enumerate(components):
                        tj = comp.tj if comp.tj is not None else comp.operation.tj
                        tpz = comp.tpz if comp.tpz is not None else comp.operation.tpz
                        tnext = comp.time_next_operation if comp.time_next_operation is not None else comp.operation.time_next_operation
                        duration = tj + tpz
                        end = order_cursor + timedelta(seconds=duration)
                        
                        item = Scheduling.objects.create(
                            order=order,
                            component=comp,
                            sequence_index=idx,
                            planned_start=order_cursor,
                            planned_end=end,
                            duration_seconds=duration,
                            buffer_seconds=tnext,
                            description=f"Auto generated for {comp.operation.number}"
                        )
                        all_created.append(item)
                        order_cursor = end + timedelta(seconds=tnext)
                    
                    if not parallel:
                        cursor = order_cursor
                        
                except Order.DoesNotExist:
                    continue
        
        ser = SchedulingSerializer(all_created, many=True)
        return Response({'items': ser.data, 'count': len(all_created)}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Update multiple schedule items at once.
        Body: {"updates": [{"id": <id>, "planned_start": "...", "planned_end": "...", ...}, ...]}
        """
        serializer = BulkSchedulingUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        updates = serializer.validated_data['updates']
        updated_items = []
        
        with transaction.atomic():
            for update_data in updates:
                item_id = update_data.pop('id')
                try:
                    item = Scheduling.objects.get(pk=item_id)
                    
                    # Update fields
                    for field, value in update_data.items():
                        if hasattr(item, field):
                            setattr(item, field, value)
                    
                    # Recalculate duration if start/end changed
                    if 'planned_start' in update_data or 'planned_end' in update_data:
                        delta = item.planned_end - item.planned_start
                        item.duration_seconds = int(delta.total_seconds())
                    
                    item.save()
                    updated_items.append(item)
                except Scheduling.DoesNotExist:
                    continue
        
        ser = SchedulingSerializer(updated_items, many=True)
        return Response({'items': ser.data, 'count': len(updated_items)})

    @action(detail=False, methods=['get'])
    def by_orders(self, request):
        """Get schedule items for specific orders.
        Query param: orders=1,2,3
        """
        orders_param = request.query_params.get('orders', '')
        if not orders_param:
            return Response({'error': 'orders parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_ids = [int(id.strip()) for id in orders_param.split(',') if id.strip()]
        qs = self.get_queryset().filter(order_id__in=order_ids).order_by('order', 'sequence_index')
        ser = SchedulingSerializer(qs, many=True)
        return Response({'items': ser.data, 'count': qs.count()})

    @action(detail=False, methods=['delete'], url_path='by_order/(?P<order_id>[^/.]+)')
    def delete_by_order(self, request, order_id=None):
        """Delete all schedule items for a specific order."""
        if not order_id:
            return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count, _ = Scheduling.objects.filter(order_id=order_id).delete()
        return Response({'deleted': deleted_count, 'order_id': order_id})

    @action(detail=False, methods=['post'])
    def check_conflicts(self, request):
        """Check for scheduling conflicts (overlapping tasks, resource conflicts, etc.)
        Body: {"items": [{"id": <id>, "start": "...", "end": "...", "workstation": ..., "production_line": ...}, ...]}
        """
        items = request.data.get('items', [])
        conflicts = []
        
        if not items:
            return Response({'conflicts': [], 'has_conflicts': False})
        
        # Check for time and resource conflicts
        for i, item1 in enumerate(items):
            for j, item2 in enumerate(items[i+1:], start=i+1):
                try:
                    start1 = timezone.datetime.fromisoformat(item1['start'].replace('Z', '+00:00'))
                    end1 = timezone.datetime.fromisoformat(item1['end'].replace('Z', '+00:00'))
                    start2 = timezone.datetime.fromisoformat(item2['start'].replace('Z', '+00:00'))
                    end2 = timezone.datetime.fromisoformat(item2['end'].replace('Z', '+00:00'))
                except (KeyError, ValueError) as e:
                    continue
                
                # Check for time overlap
                has_time_overlap = start1 < end2 and start2 < end1
                
                if has_time_overlap:
                    # Check if they use the same resource
                    same_workstation = (
                        item1.get('workstation') and 
                        item2.get('workstation') and 
                        item1.get('workstation') == item2.get('workstation')
                    )
                    
                    same_production_line = (
                        item1.get('production_line') and 
                        item2.get('production_line') and 
                        item1.get('production_line') == item2.get('production_line')
                    )
                    
                    if same_workstation or same_production_line:
                        conflict_type = 'workstation_conflict' if same_workstation else 'production_line_conflict'
                        conflicts.append({
                            'task1': {
                                'id': item1.get('id'),
                                'order': item1.get('order'),
                                'operation': item1.get('operation'),
                                'start': item1.get('start'),
                                'end': item1.get('end'),
                            },
                            'task2': {
                                'id': item2.get('id'),
                                'order': item2.get('order'),
                                'operation': item2.get('operation'),
                                'start': item2.get('start'),
                                'end': item2.get('end'),
                            },
                            'type': conflict_type,
                            'resource': item1.get('workstation') if same_workstation else item1.get('production_line'),
                            'overlap_start': max(start1, start2).isoformat(),
                            'overlap_end': min(end1, end2).isoformat()
                        })
        
        return Response({'conflicts': conflicts, 'has_conflicts': len(conflicts) > 0})

    @action(detail=False, methods=['post'])
    def optimize(self, request):
        """Optimize schedule for given orders using various algorithms.
        Body: {"orders": [<order_id>, ...], "method": "earliest|latest|balanced"}
        """
        order_ids = request.data.get('orders', [])
        method = request.data.get('method', 'earliest')
        
        if not order_ids:
            return Response({'error': 'orders list required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all schedule items for these orders
        items = Scheduling.objects.filter(order_id__in=order_ids).select_related('order', 'component')
        
        # Simple optimization: reorder by earliest deadline, priority, etc.
        # This is a placeholder - real optimization would be more complex
        if method == 'earliest':
            items = items.order_by('order__deadline', 'sequence_index')
        elif method == 'latest':
            items = items.order_by('-order__deadline', 'sequence_index')
        else:  # balanced
            items = items.order_by('order__priority', 'sequence_index')
        
        # Regenerate schedule with optimized order
        cursor = timezone.now()
        updated_items = []
        
        with transaction.atomic():
            for item in items:
                duration = item.duration_seconds
                end = cursor + timedelta(seconds=duration)
                
                item.planned_start = cursor
                item.planned_end = end
                item.save()
                updated_items.append(item)
                
                cursor = end + timedelta(seconds=item.buffer_seconds)
        
        ser = SchedulingSerializer(updated_items, many=True)
        return Response({'items': ser.data, 'count': len(updated_items)})
