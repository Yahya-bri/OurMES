from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Sum, F
from ..domain.models import ProductionCounting
from .serializers import ProductionCountingSerializer
from mes.plugins.orders.domain.models import Order


class ProductionCountingViewSet(viewsets.ModelViewSet):
    queryset = ProductionCounting.objects.select_related(
        'order', 'operation', 'component', 'product', 'workstation'
    )
    serializer_class = ProductionCountingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        order_param = self.request.query_params.get('order') or self.request.query_params.get('order_id')
        order_in_param = self.request.query_params.get('order__in')
        workstation_param = self.request.query_params.get('workstation')
        if status_param:
            qs = qs.filter(status=status_param)
        if order_param:
            qs = qs.filter(order_id=order_param)
        elif order_in_param:
            order_ids = [
                int(order_id.strip()) for order_id in order_in_param.split(',')
                if order_id.strip().isdigit()
            ]
            if order_ids:
                qs = qs.filter(order_id__in=order_ids)
        if workstation_param:
            qs = qs.filter(workstation_id=workstation_param)
        return qs

    def _assert_workstation_matches_order(self, order, workstation):
        if order and workstation and order.production_line_id and workstation.production_line_id:
            if order.production_line_id != workstation.production_line_id:
                raise ValidationError("Workstation must belong to the order's production line.")

    def perform_create(self, serializer):
        # default start_time if creating in_progress without provided start_time
        validated = serializer.validated_data
        start_time = validated.get('start_time')
        status_val = validated.get('status', 'in_progress')
        self._assert_workstation_matches_order(
            validated.get('order'),
            validated.get('workstation')
        )
        if status_val == 'in_progress' and start_time is None:
            from django.utils import timezone
            instance = serializer.save(start_time=timezone.now())
        else:
            instance = serializer.save()
        # Ensure order transitions to in_progress if first production record
        order = instance.order
        if order.state not in ['in_progress', 'completed', 'abandoned', 'interrupted']:
            order.state = 'in_progress'
            from django.utils import timezone
            if order.start_date is None:
                order.start_date = timezone.now()
            order.save(update_fields=['state', 'start_date'])
        self._update_order_done_quantity(instance.order)

    def perform_update(self, serializer):
        validated = serializer.validated_data
        workstation = validated.get('workstation') or serializer.instance.workstation
        order = serializer.instance.order
        self._assert_workstation_matches_order(order, workstation)
        instance = serializer.save()
        self._update_order_done_quantity(instance.order)

    def perform_destroy(self, instance):
        order = instance.order
        instance.delete()
        self._update_order_done_quantity(order)

    def _update_order_done_quantity(self, order):
        agg = order.production_counts.aggregate(total=Sum('done_quantity'))
        order.done_quantity = agg['total'] or 0
        order.save(update_fields=['done_quantity'])

    @action(detail=False, methods=['get'])
    def order_progress(self, request):
        """Return progress summary for an order given ?order=<id>:
        - planned_quantity
        - done_quantity
        - percent_done
        - per operation breakdown
        """
        order_id = request.query_params.get('order') or request.query_params.get('order_id')
        if not order_id:
            return Response({'error': 'order query param required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'order not found'}, status=status.HTTP_404_NOT_FOUND)
        by_operation = order.production_counts.values(
            op=F('operation__number')
        ).annotate(done=Sum('done_quantity'), scrap=Sum('rejected_quantity')).order_by('op')
        planned = order.planned_quantity
        done = order.done_quantity
        percent = float(done / planned * 100) if planned and planned > 0 else 0.0
        return Response({
            'order': order.number,
            'planned_quantity': str(planned),
            'done_quantity': str(done),
            'percent_done': round(percent, 2),
            'operations': [
                {
                    'operation': row['op'],
                    'done_quantity': str(row['done'] or 0),
                    'scrap_quantity': str(row['scrap'] or 0)
                } for row in by_operation if row['op'] is not None
            ]
        })

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        record = self.get_object()
        produced = request.data.get('produced_quantity')
        scrap = request.data.get('scrap_quantity')
        from django.utils import timezone
        if produced is not None:
            record.done_quantity = produced
        if scrap is not None:
            record.rejected_quantity = scrap
        record.end_time = timezone.now()
        record.status = 'completed'
        record.save()
        self._update_order_done_quantity(record.order)
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        record = self.get_object()
        produced = request.data.get('produced_quantity')
        scrap = request.data.get('scrap_quantity')
        if produced is not None:
            record.done_quantity = produced
        if scrap is not None:
            record.rejected_quantity = scrap
        record.save(update_fields=['done_quantity', 'rejected_quantity'])
        self._update_order_done_quantity(record.order)
        return Response(self.get_serializer(record).data)
