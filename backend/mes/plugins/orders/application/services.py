from django.core.exceptions import ValidationError
from django.db import transaction
from ..domain.models import Order, OrderStateChange


class OrderWorkflowService:
    """Application layer that orchestrates order state transitions and stats."""

    @staticmethod
    def _validate_state(target_state: str) -> str:
        valid_states = dict(Order.STATE_CHOICES)
        if target_state not in valid_states:
            raise ValidationError(f"Invalid state '{target_state}'")
        return target_state

    @classmethod
    @transaction.atomic
    def change_state(cls, order: Order, target_state: str, worker: str = '') -> OrderStateChange:
        """Persist a state change event and update the order atomically."""
        desired_state = cls._validate_state(target_state)
        change = OrderStateChange.objects.create(
            order=order,
            source_state=order.state,
            target_state=desired_state,
            worker=worker or '',
        )
        order.state = desired_state
        order.save(update_fields=['state', 'updated_at'])
        return change

    @staticmethod
    def dashboard_stats():
        """Aggregate counts for the dashboard widget."""
        qs = Order.objects.filter(active=True)
        return {
            'total': qs.count(),
            'pending': qs.filter(state='pending').count(),
            'in_progress': qs.filter(state='in_progress').count(),
            'completed': qs.filter(state='completed').count(),
        }
