"""
Production Counting Services.

Business logic for tracking production progress, recording output,
and managing production records.
"""
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Count, Q, F
from django.utils import timezone

from core.base.services import BaseService, StatefulService
from core.base.exceptions import ValidationException, BusinessRuleException
from ..domain.models import ProductionCounting


class ProductionCountingService(StatefulService):
    """Service for managing production counting records."""
    model = ProductionCounting
    state_field = 'status'
    valid_transitions = {
        'in_progress': ['completed'],
        'completed': [],  # Cannot change completed records
    }

    @classmethod
    def get_by_order(cls, order_id: int):
        """Get all production counts for an order."""
        return cls.get_queryset().filter(order_id=order_id)

    @classmethod
    def get_by_workstation(cls, workstation_id: int):
        """Get production counts for a specific workstation."""
        return cls.get_queryset().filter(workstation_id=workstation_id)

    @classmethod
    def get_by_operator(cls, operator_id: int):
        """Get production counts for a specific operator."""
        return cls.get_queryset().filter(operator_id=operator_id)

    @classmethod
    def get_active_records(cls, workstation_id: int = None):
        """Get currently active (in_progress) production records."""
        queryset = cls.get_queryset().filter(status='in_progress')
        if workstation_id:
            queryset = queryset.filter(workstation_id=workstation_id)
        return queryset

    @classmethod
    @transaction.atomic
    def start_production(
        cls,
        order_id: int,
        operation_id: int = None,
        component_id: int = None,
        product_id: int = None,
        workstation_id: int = None,
        operator_id: int = None
    ) -> ProductionCounting:
        """
        Start a new production counting record.

        Records the start time and sets status to in_progress.
        """
        # Check if there's already an active record for this order/operation
        existing = cls.get_queryset().filter(
            order_id=order_id,
            operation_id=operation_id,
            workstation_id=workstation_id,
            status='in_progress'
        ).first()

        if existing:
            raise BusinessRuleException(
                'ACTIVE_RECORD_EXISTS',
                f'Production already in progress for this order/operation at workstation'
            )

        return cls.model.objects.create(
            order_id=order_id,
            operation_id=operation_id,
            component_id=component_id,
            product_id=product_id,
            workstation_id=workstation_id,
            operator_id=operator_id,
            start_time=timezone.now(),
            status='in_progress'
        )

    @classmethod
    @transaction.atomic
    def record_output(
        cls,
        record: ProductionCounting,
        done_quantity: Decimal,
        rejected_quantity: Decimal = Decimal('0')
    ) -> ProductionCounting:
        """
        Record production output quantities.

        Can be called multiple times for partial progress updates.
        """
        if record.status == 'completed':
            raise BusinessRuleException(
                'RECORD_COMPLETED',
                'Cannot update completed production record'
            )

        if done_quantity < 0 or rejected_quantity < 0:
            raise ValidationException(
                'Quantities cannot be negative',
                field='quantity'
            )

        record.done_quantity = done_quantity
        record.rejected_quantity = rejected_quantity
        record.save(update_fields=['done_quantity', 'rejected_quantity', 'updated_at'])
        return record

    @classmethod
    @transaction.atomic
    def complete_production(
        cls,
        record: ProductionCounting,
        done_quantity: Decimal = None,
        rejected_quantity: Decimal = None
    ) -> ProductionCounting:
        """
        Complete a production counting record.

        Records end time and optionally updates final quantities.
        """
        if done_quantity is not None:
            record.done_quantity = done_quantity
        if rejected_quantity is not None:
            record.rejected_quantity = rejected_quantity

        record.end_time = timezone.now()
        record.status = 'completed'
        record.save(update_fields=[
            'done_quantity', 'rejected_quantity', 'end_time', 'status', 'updated_at'
        ])
        return record

    @classmethod
    def get_order_progress(cls, order_id: int) -> dict:
        """
        Get production progress summary for an order.

        Returns total done, rejected, and progress by operation.
        """
        records = cls.get_by_order(order_id)

        totals = records.aggregate(
            total_done=Sum('done_quantity'),
            total_rejected=Sum('rejected_quantity')
        )

        by_operation = records.values('operation__number', 'operation__name').annotate(
            done=Sum('done_quantity'),
            rejected=Sum('rejected_quantity'),
            record_count=Count('id')
        )

        return {
            'order_id': order_id,
            'total_done': totals['total_done'] or Decimal('0'),
            'total_rejected': totals['total_rejected'] or Decimal('0'),
            'net_quantity': (totals['total_done'] or Decimal('0')) - (totals['total_rejected'] or Decimal('0')),
            'by_operation': list(by_operation)
        }

    @classmethod
    def get_workstation_performance(cls, workstation_id: int, days: int = 7) -> dict:
        """
        Get performance metrics for a workstation.
        """
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)

        records = cls.get_queryset().filter(
            workstation_id=workstation_id,
            timestamp__gte=cutoff
        )

        metrics = records.aggregate(
            total_done=Sum('done_quantity'),
            total_rejected=Sum('rejected_quantity'),
            record_count=Count('id'),
            completed_count=Count('id', filter=Q(status='completed'))
        )

        total_done = metrics['total_done'] or Decimal('0')
        total_rejected = metrics['rejected_quantity'] or Decimal('0')

        return {
            'workstation_id': workstation_id,
            'period_days': days,
            'total_done': total_done,
            'total_rejected': total_rejected,
            'reject_rate': float(total_rejected / total_done * 100) if total_done > 0 else 0,
            'record_count': metrics['record_count'],
            'completion_rate': float(
                metrics['completed_count'] / metrics['record_count'] * 100
            ) if metrics['record_count'] > 0 else 0
        }

    @classmethod
    def get_operator_performance(cls, operator_id: int, days: int = 7) -> dict:
        """Get performance metrics for an operator."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)

        records = cls.get_queryset().filter(
            operator_id=operator_id,
            timestamp__gte=cutoff
        )

        metrics = records.aggregate(
            total_done=Sum('done_quantity'),
            total_rejected=Sum('rejected_quantity'),
            record_count=Count('id')
        )

        return {
            'operator_id': operator_id,
            'period_days': days,
            'total_done': metrics['total_done'] or Decimal('0'),
            'total_rejected': metrics['total_rejected'] or Decimal('0'),
            'record_count': metrics['record_count']
        }

    @classmethod
    def stats(cls):
        """Get overall production counting statistics."""
        today = timezone.now().date()
        return cls.get_queryset().aggregate(
            total_records=Count('id'),
            in_progress=Count('id', filter=Q(status='in_progress')),
            completed=Count('id', filter=Q(status='completed')),
            today_records=Count('id', filter=Q(timestamp__date=today)),
            total_done=Sum('done_quantity'),
            total_rejected=Sum('rejected_quantity'),
        )
