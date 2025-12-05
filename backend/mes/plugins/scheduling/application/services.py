"""
Production Scheduling Services.

Business logic for production scheduling, conflict detection,
and schedule optimization.
"""
from datetime import timedelta
from django.db import transaction
from django.db.models import Count, Q, F, Min, Max
from django.utils import timezone

from core.base.services import BaseService
from core.base.exceptions import ValidationException, BusinessRuleException
from ..domain.models import Scheduling


class SchedulingService(BaseService):
    """Service for managing production schedules."""
    model = Scheduling

    @classmethod
    def get_by_order(cls, order_id: int):
        """Get all schedule items for an order."""
        return cls.get_queryset().filter(order_id=order_id).order_by('sequence_index')

    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """Get schedule items within a date range."""
        return cls.get_queryset().filter(
            planned_start__lte=end_date,
            planned_end__gte=start_date
        ).order_by('planned_start')

    @classmethod
    def get_locked_items(cls):
        """Get all locked schedule items."""
        return cls.get_queryset().filter(locked=True)

    @classmethod
    def get_unlocked_items(cls):
        """Get all unlocked schedule items."""
        return cls.get_queryset().filter(locked=False)

    @classmethod
    @transaction.atomic
    def create_schedule_item(
        cls,
        order_id: int,
        component_id: int,
        planned_start,
        duration_seconds: int,
        buffer_seconds: int = 0,
        sequence_index: int = None,
        description: str = ''
    ) -> Scheduling:
        """
        Create a new schedule item.

        Automatically calculates planned_end from start and duration.
        """
        if duration_seconds <= 0:
            raise ValidationException(
                'Duration must be positive',
                field='duration_seconds'
            )

        planned_end = planned_start + timedelta(seconds=duration_seconds + buffer_seconds)

        # Auto-assign sequence if not provided
        if sequence_index is None:
            max_seq = cls.get_by_order(order_id).aggregate(
                max_seq=Max('sequence_index')
            )['max_seq']
            sequence_index = (max_seq or 0) + 1

        return cls.model.objects.create(
            order_id=order_id,
            component_id=component_id,
            planned_start=planned_start,
            planned_end=planned_end,
            duration_seconds=duration_seconds,
            buffer_seconds=buffer_seconds,
            sequence_index=sequence_index,
            description=description
        )

    @classmethod
    @transaction.atomic
    def reschedule(
        cls,
        schedule_item: Scheduling,
        new_start,
        new_duration: int = None
    ) -> Scheduling:
        """
        Reschedule an item to a new time.

        Locked items cannot be rescheduled.
        """
        if schedule_item.locked:
            raise BusinessRuleException(
                'ITEM_LOCKED',
                'Cannot reschedule a locked item'
            )

        duration = new_duration or schedule_item.duration_seconds
        new_end = new_start + timedelta(seconds=duration + schedule_item.buffer_seconds)

        schedule_item.planned_start = new_start
        schedule_item.planned_end = new_end
        if new_duration:
            schedule_item.duration_seconds = new_duration
        schedule_item.save(update_fields=[
            'planned_start', 'planned_end', 'duration_seconds'
        ])
        return schedule_item

    @classmethod
    @transaction.atomic
    def lock_item(cls, schedule_item: Scheduling) -> Scheduling:
        """Lock a schedule item to prevent changes."""
        schedule_item.locked = True
        schedule_item.save(update_fields=['locked'])
        return schedule_item

    @classmethod
    @transaction.atomic
    def unlock_item(cls, schedule_item: Scheduling) -> Scheduling:
        """Unlock a schedule item to allow changes."""
        schedule_item.locked = False
        schedule_item.save(update_fields=['locked'])
        return schedule_item

    @classmethod
    @transaction.atomic
    def lock_order_items(cls, order_id: int) -> int:
        """Lock all schedule items for an order."""
        return cls.get_by_order(order_id).update(locked=True)

    @classmethod
    @transaction.atomic
    def unlock_order_items(cls, order_id: int) -> int:
        """Unlock all schedule items for an order."""
        return cls.get_by_order(order_id).update(locked=False)

    @classmethod
    def detect_conflicts(cls, start_date=None, end_date=None) -> list:
        """
        Detect scheduling conflicts (overlapping items).

        A conflict occurs when two items for the same resource
        (workstation/component) overlap in time.
        """
        if not start_date:
            start_date = timezone.now()
        if not end_date:
            end_date = start_date + timedelta(days=30)

        items = list(cls.get_by_date_range(start_date, end_date).select_related(
            'order', 'component', 'component__operation'
        ))

        conflicts = []
        for i, item1 in enumerate(items):
            for item2 in items[i + 1:]:
                # Check if same workstation/operation and times overlap
                if item1.component_id == item2.component_id:
                    if (item1.planned_start < item2.planned_end and
                            item1.planned_end > item2.planned_start):
                        conflicts.append({
                            'item1': {
                                'id': item1.id,
                                'order': item1.order.number,
                                'start': item1.planned_start.isoformat(),
                                'end': item1.planned_end.isoformat()
                            },
                            'item2': {
                                'id': item2.id,
                                'order': item2.order.number,
                                'start': item2.planned_start.isoformat(),
                                'end': item2.planned_end.isoformat()
                            },
                            'overlap_type': 'same_component'
                        })

        return conflicts

    @classmethod
    @transaction.atomic
    def shift_order_schedule(cls, order_id: int, delta_seconds: int) -> int:
        """
        Shift all unlocked schedule items for an order by a time delta.

        Positive delta moves forward, negative moves backward.
        """
        delta = timedelta(seconds=delta_seconds)
        items = cls.get_by_order(order_id).filter(locked=False)

        count = 0
        for item in items:
            item.planned_start = item.planned_start + delta
            item.planned_end = item.planned_end + delta
            item.save(update_fields=['planned_start', 'planned_end'])
            count += 1

        return count

    @classmethod
    def get_order_schedule_summary(cls, order_id: int) -> dict:
        """Get schedule summary for an order."""
        items = cls.get_by_order(order_id)

        if not items.exists():
            return {
                'order_id': order_id,
                'has_schedule': False
            }

        summary = items.aggregate(
            earliest_start=Min('planned_start'),
            latest_end=Max('planned_end'),
            total_duration=Sum('duration_seconds'),
            total_buffer=Sum('buffer_seconds'),
            item_count=Count('id'),
            locked_count=Count('id', filter=Q(locked=True))
        )

        return {
            'order_id': order_id,
            'has_schedule': True,
            'earliest_start': summary['earliest_start'],
            'latest_end': summary['latest_end'],
            'total_duration_hours': round(summary['total_duration'] / 3600, 2),
            'total_buffer_hours': round(summary['total_buffer'] / 3600, 2),
            'item_count': summary['item_count'],
            'locked_count': summary['locked_count']
        }

    @classmethod
    @transaction.atomic
    def generate_schedule_from_technology(
        cls,
        order_id: int,
        start_time,
        clear_existing: bool = False
    ) -> list:
        """
        Generate schedule items from order's technology tree.

        Uses operation durations (tj, tpz) to calculate timing.
        """
        from mes.plugins.orders.domain.models import Order

        order = Order.objects.select_related('technology').get(id=order_id)
        if not order.technology_id:
            raise BusinessRuleException(
                'NO_TECHNOLOGY',
                'Order has no technology assigned'
            )

        if clear_existing:
            cls.get_by_order(order_id).filter(locked=False).delete()

        components = order.technology.operation_components.select_related(
            'operation'
        ).order_by('node_number')

        created_items = []
        current_time = start_time

        for idx, comp in enumerate(components):
            # Calculate duration from operation times
            tj = comp.tj or comp.operation.tj or 0
            tpz = comp.tpz or comp.operation.tpz or 0
            time_next = comp.time_next_operation or comp.operation.time_next_operation or 0

            # Duration in seconds (assuming tj/tpz are in minutes)
            duration_seconds = int((tj + tpz) * 60)
            buffer_seconds = int(time_next * 60)

            item = cls.create_schedule_item(
                order_id=order_id,
                component_id=comp.id,
                planned_start=current_time,
                duration_seconds=duration_seconds,
                buffer_seconds=buffer_seconds,
                sequence_index=idx,
                description=f"Operation: {comp.operation.number} - {comp.operation.name}"
            )
            created_items.append(item)

            # Move time forward for next operation
            current_time = item.planned_end

        return created_items

    @classmethod
    def stats(cls):
        """Get scheduling statistics."""
        today = timezone.now().date()
        this_week_start = timezone.now() - timedelta(days=timezone.now().weekday())

        return cls.get_queryset().aggregate(
            total=Count('id'),
            locked=Count('id', filter=Q(locked=True)),
            unlocked=Count('id', filter=Q(locked=False)),
            today=Count('id', filter=Q(planned_start__date=today)),
            this_week=Count('id', filter=Q(planned_start__gte=this_week_start)),
            overdue=Count('id', filter=Q(planned_end__lt=timezone.now())),
        )
