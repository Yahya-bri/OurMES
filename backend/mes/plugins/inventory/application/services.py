"""
Inventory Management Services.

Business logic for stock management, container tracking, traceability,
and kanban replenishment.
"""
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, F, Q
from django.utils import timezone

from core.base.services import BaseService, StatefulService
from core.base.exceptions import ValidationException, BusinessRuleException
from ..domain.models import MaterialStock, Container, TraceabilityRecord, KanbanCard


class StockService(BaseService):
    """Service for managing material stock levels."""
    model = MaterialStock

    @classmethod
    def get_by_material(cls, material_id: int):
        """Get all stock records for a material across locations."""
        return cls.get_queryset().filter(material_id=material_id)

    @classmethod
    def get_total_quantity(cls, material_id: int) -> Decimal:
        """Get total quantity of a material across all locations."""
        result = cls.get_by_material(material_id).aggregate(
            total=Sum('quantity')
        )
        return result['total'] or Decimal('0')

    @classmethod
    def get_by_location(cls, location_type: str = None, location_name: str = None):
        """Get stock at a specific location."""
        queryset = cls.get_queryset()
        if location_type:
            queryset = queryset.filter(location_type=location_type)
        if location_name:
            queryset = queryset.filter(location_name=location_name)
        return queryset

    @classmethod
    @transaction.atomic
    def adjust_quantity(
        cls,
        material_id: int,
        location_name: str,
        quantity_change: Decimal,
        batch_number: str = None,
        reason: str = ''
    ) -> MaterialStock:
        """
        Adjust stock quantity (positive or negative).

        Creates stock record if it doesn't exist.
        """
        stock, created = cls.model.objects.get_or_create(
            material_id=material_id,
            location_name=location_name,
            batch_number=batch_number,
            defaults={'quantity': Decimal('0'), 'location_type': 'warehouse'}
        )

        new_quantity = stock.quantity + quantity_change

        if new_quantity < 0:
            raise BusinessRuleException(
                'INSUFFICIENT_STOCK',
                f'Cannot reduce stock below zero. Current: {stock.quantity}, Change: {quantity_change}'
            )

        stock.quantity = new_quantity
        stock.save(update_fields=['quantity', 'updated_at'])
        return stock

    @classmethod
    @transaction.atomic
    def transfer(
        cls,
        material_id: int,
        from_location: str,
        to_location: str,
        quantity: Decimal,
        batch_number: str = None
    ) -> tuple:
        """Transfer stock between locations."""
        if quantity <= 0:
            raise ValidationException(
                'Transfer quantity must be positive',
                field='quantity'
            )

        # Deduct from source
        from_stock = cls.adjust_quantity(
            material_id, from_location, -quantity, batch_number
        )

        # Add to destination
        to_stock = cls.adjust_quantity(
            material_id, to_location, quantity, batch_number
        )

        return from_stock, to_stock

    @classmethod
    def get_low_stock_items(cls, threshold_percentage: int = 20):
        """
        Get items with stock below threshold.

        This would need a min_stock_level field on Product or MaterialStock.
        For now, returns items with zero or negative stock.
        """
        return cls.get_queryset().filter(quantity__lte=0)

    @classmethod
    def get_expiring_stock(cls, days: int = 30):
        """Get stock items expiring within specified days."""
        from datetime import timedelta
        cutoff = timezone.now().date() + timedelta(days=days)

        return cls.get_queryset().filter(
            expiry_date__isnull=False,
            expiry_date__lte=cutoff
        ).order_by('expiry_date')


class ContainerService(BaseService):
    """Service for managing containers and their contents."""
    model = Container

    @classmethod
    def get_by_id(cls, container_id: str):
        """Get container by its unique ID."""
        return cls.get_queryset().filter(container_id=container_id).first()

    @classmethod
    def get_by_location(cls, location: str):
        """Get all containers at a location."""
        return cls.get_queryset().filter(location=location)

    @classmethod
    def get_by_material(cls, material_id: int):
        """Get all containers holding a specific material."""
        return cls.get_queryset().filter(content_material_id=material_id)

    @classmethod
    @transaction.atomic
    def fill_container(
        cls,
        container_id: str,
        material_id: int,
        quantity: Decimal
    ) -> Container:
        """Fill a container with material."""
        container = cls.get_by_id(container_id)
        if not container:
            raise ValidationException(
                f'Container {container_id} not found',
                field='container_id'
            )

        if container.content_material_id and container.content_quantity > 0:
            raise BusinessRuleException(
                'CONTAINER_NOT_EMPTY',
                f'Container {container_id} already contains material'
            )

        container.content_material_id = material_id
        container.content_quantity = quantity
        container.save(update_fields=['content_material_id', 'content_quantity', 'updated_at'])
        return container

    @classmethod
    @transaction.atomic
    def empty_container(cls, container_id: str) -> Container:
        """Empty a container."""
        container = cls.get_by_id(container_id)
        if not container:
            raise ValidationException(
                f'Container {container_id} not found',
                field='container_id'
            )

        container.content_material_id = None
        container.content_quantity = Decimal('0')
        container.save(update_fields=['content_material_id', 'content_quantity', 'updated_at'])
        return container

    @classmethod
    @transaction.atomic
    def move_container(cls, container_id: str, new_location: str) -> Container:
        """Move a container to a new location."""
        container = cls.get_by_id(container_id)
        if not container:
            raise ValidationException(
                f'Container {container_id} not found',
                field='container_id'
            )

        container.location = new_location
        container.save(update_fields=['location', 'updated_at'])
        return container


class TraceabilityService(BaseService):
    """Service for material traceability and genealogy."""
    model = TraceabilityRecord

    @classmethod
    @transaction.atomic
    def record_consumption(
        cls,
        finished_good_id: int,
        finished_good_batch: str,
        raw_material_id: int,
        raw_material_batch: str,
        quantity_used: Decimal
    ) -> TraceabilityRecord:
        """Record material consumption for traceability."""
        return cls.model.objects.create(
            finished_good_id=finished_good_id,
            finished_good_batch=finished_good_batch,
            raw_material_id=raw_material_id,
            raw_material_batch=raw_material_batch,
            quantity_used=quantity_used
        )

    @classmethod
    def trace_forward(cls, raw_material_batch: str):
        """
        Forward traceability: find all finished goods that used a raw material batch.
        """
        return cls.get_queryset().filter(
            raw_material_batch=raw_material_batch
        ).select_related('finished_good', 'raw_material')

    @classmethod
    def trace_backward(cls, finished_good_batch: str):
        """
        Backward traceability: find all raw materials used in a finished good batch.
        """
        return cls.get_queryset().filter(
            finished_good_batch=finished_good_batch
        ).select_related('finished_good', 'raw_material')

    @classmethod
    def get_affected_batches(cls, raw_material_batch: str) -> list:
        """
        Get all affected finished good batches for a recall scenario.
        """
        records = cls.trace_forward(raw_material_batch)
        return list(records.values_list('finished_good_batch', flat=True).distinct())

    @classmethod
    def get_genealogy(cls, finished_good_batch: str) -> dict:
        """
        Get complete genealogy for a finished good batch.

        Returns hierarchical structure of all raw materials used.
        """
        records = cls.trace_backward(finished_good_batch)

        return {
            'batch': finished_good_batch,
            'components': [
                {
                    'material_number': r.raw_material.number,
                    'material_name': r.raw_material.name,
                    'batch': r.raw_material_batch,
                    'quantity_used': str(r.quantity_used),
                    'timestamp': r.timestamp.isoformat()
                }
                for r in records
            ]
        }


class KanbanService(StatefulService):
    """Service for kanban card management and replenishment."""
    model = KanbanCard
    state_field = 'status'
    valid_transitions = {
        'full': ['replenishing', 'empty'],
        'replenishing': ['full'],
        'empty': ['replenishing'],
    }

    @classmethod
    def get_by_location(cls, location: str):
        """Get all kanban cards at a location."""
        return cls.get_queryset().filter(location=location)

    @classmethod
    def get_by_material(cls, material_id: int):
        """Get all kanban cards for a material."""
        return cls.get_queryset().filter(material_id=material_id)

    @classmethod
    def get_cards_needing_replenishment(cls):
        """Get all kanban cards in empty or replenishing status."""
        return cls.get_queryset().filter(
            status__in=['empty', 'replenishing']
        ).select_related('material')

    @classmethod
    @transaction.atomic
    def trigger_replenishment(cls, kanban_card: KanbanCard) -> KanbanCard:
        """
        Trigger replenishment for a kanban card.

        Changes status to 'replenishing' and could trigger
        notifications or production orders.
        """
        if kanban_card.status == 'full':
            raise BusinessRuleException(
                'CARD_FULL',
                'Cannot trigger replenishment for a full kanban card'
            )

        return cls.change_state(kanban_card, 'replenishing')

    @classmethod
    @transaction.atomic
    def complete_replenishment(cls, kanban_card: KanbanCard) -> KanbanCard:
        """Mark kanban card as replenished (full)."""
        kanban_card.last_replenished = timezone.now()
        kanban_card.save(update_fields=['last_replenished'])
        return cls.change_state(kanban_card, 'full')

    @classmethod
    @transaction.atomic
    def mark_empty(cls, kanban_card: KanbanCard, auto_trigger: bool = True) -> KanbanCard:
        """
        Mark kanban card as empty.

        If auto_trigger is True, automatically triggers replenishment.
        """
        card = cls.change_state(kanban_card, 'empty')

        if auto_trigger:
            card = cls.trigger_replenishment(card)

        return card

    @classmethod
    def stats(cls):
        """Get kanban system statistics."""
        from core.utils.query_utils import get_stats_aggregation
        return get_stats_aggregation(
            cls.get_queryset(),
            'status',
            cls.model.STATUS_CHOICES
        )
