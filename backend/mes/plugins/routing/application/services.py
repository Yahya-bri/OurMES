"""
Routing/Technology Management Services.

Business logic for managing manufacturing technologies (routings),
operations, and their relationships.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, Q

from core.base.services import BaseService, StatefulService
from core.base.exceptions import ValidationException, StateTransitionException
from ..domain.models import (
    Technology, Operation, TechnologyOperationComponent,
    OperationProductInComponent, OperationProductOutComponent
)


class TechnologyService(StatefulService):
    """Service for managing technologies (routings)."""
    model = Technology
    state_field = 'state'
    valid_transitions = {
        'draft': ['accepted', 'declined'],
        'accepted': ['checked', 'declined', 'outdated'],
        'checked': ['outdated', 'declined'],
        'outdated': ['draft'],  # Can be revised
        'declined': ['draft'],  # Can be revised
    }

    @classmethod
    def get_active(cls):
        """Get all active technologies."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def get_by_product(cls, product_id: int):
        """Get all technologies for a product."""
        return cls.get_queryset().filter(product_id=product_id)

    @classmethod
    def get_master_for_product(cls, product_id: int):
        """Get the master technology for a product."""
        return cls.get_queryset().filter(
            product_id=product_id,
            master=True
        ).first()

    @classmethod
    @transaction.atomic
    def change_state(cls, technology: Technology, new_state: str) -> Technology:
        """Change technology state with validation."""
        valid_states = dict(Technology.STATE_CHOICES)
        if new_state not in valid_states:
            raise ValidationException(
                f"Invalid state '{new_state}'. Must be one of: {', '.join(valid_states.keys())}",
                field='state'
            )

        current_state = technology.state
        if cls.valid_transitions and not cls.validate_transition(current_state, new_state):
            raise StateTransitionException('Technology', current_state, new_state)

        technology.state = new_state
        technology.save(update_fields=['state', 'updated_at'])
        return technology

    @classmethod
    @transaction.atomic
    def bulk_change_state(cls, ids: list, new_state: str) -> int:
        """Bulk change state for multiple technologies."""
        valid_states = dict(Technology.STATE_CHOICES)
        if new_state not in valid_states:
            raise ValidationException(
                f"Invalid state '{new_state}'",
                field='state'
            )
        return cls.get_queryset().filter(id__in=ids).update(state=new_state)

    @classmethod
    @transaction.atomic
    def bulk_activate(cls, ids: list) -> int:
        """Activate multiple technologies."""
        return cls.get_queryset().filter(id__in=ids).update(active=True)

    @classmethod
    @transaction.atomic
    def bulk_deactivate(cls, ids: list) -> int:
        """Deactivate multiple technologies."""
        return cls.get_queryset().filter(id__in=ids).update(active=False)

    @classmethod
    @transaction.atomic
    def set_master(cls, technology: Technology) -> Technology:
        """
        Set this technology as master for its product.

        Only one technology can be master per product.
        """
        Technology.objects.filter(
            product=technology.product,
            master=True
        ).exclude(id=technology.id).update(master=False)

        technology.master = True
        technology.save(update_fields=['master', 'updated_at'])
        return technology

    @classmethod
    def build_operation_tree(cls, technology: Technology) -> dict:
        """
        Build hierarchical operation tree for a technology.

        Returns structured tree with operations, inputs/outputs, and timing summary.
        """
        components = technology.operation_components.select_related(
            'operation', 'parent'
        ).prefetch_related(
            'input_products__product',
            'output_products__product',
            'operation__workstations'
        ).order_by('node_number')

        def effective_val(component, field):
            """Get effective value with fallback to operation default."""
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
                    'id': comp.operation.id,
                    'number': comp.operation.number,
                    'name': comp.operation.name,
                    'workstations': [
                        {'id': w.id, 'number': w.number}
                        for w in comp.operation.workstations.all()
                    ],
                    'tj': tj,
                    'tpz': tpz,
                    'time_next_operation': tnext,
                },
                'input_products': [
                    {
                        'id': ip.product.id,
                        'number': ip.product.number,
                        'name': ip.product.name,
                        'quantity': str(ip.quantity)
                    }
                    for ip in comp.input_products.all()
                ],
                'output_products': [
                    {
                        'id': op.product.id,
                        'number': op.product.number,
                        'name': op.product.name,
                        'quantity': str(op.quantity)
                    }
                    for op in comp.output_products.all()
                ]
            })

        return {
            'technology': {
                'id': technology.id,
                'number': technology.number,
                'name': technology.name,
                'product': technology.product.number if technology.product_id else None,
                'state': technology.state,
            },
            'summary': {
                'total_tj': total_tj,
                'total_tpz': total_tpz,
                'total_time_next_operation': total_next,
                'total_time': total_tj + total_tpz + total_next,
                'nodes': len(tree_nodes)
            },
            'tree': tree_nodes
        }

    @classmethod
    def stats(cls):
        """
        Get technology statistics using optimized aggregation.

        Uses single query with conditional counts instead of multiple queries.
        """
        return cls.get_queryset().aggregate(
            total=Count('id'),
            draft=Count('id', filter=Q(state='draft')),
            accepted=Count('id', filter=Q(state='accepted')),
            checked=Count('id', filter=Q(state='checked')),
            outdated=Count('id', filter=Q(state='outdated')),
            declined=Count('id', filter=Q(state='declined')),
            master=Count('id', filter=Q(master=True)),
            active=Count('id', filter=Q(active=True)),
        )


class OperationService(BaseService):
    """Service for managing operations."""
    model = Operation

    @classmethod
    def get_active(cls):
        """Get all active operations."""
        return cls.get_queryset().filter(active=True)

    @classmethod
    def get_by_workstation(cls, workstation_id: int):
        """Get operations that can be performed at a workstation."""
        return cls.get_active().filter(workstations__id=workstation_id)

    @classmethod
    def search(cls, query: str):
        """Search operations by number or name."""
        return cls.get_queryset().filter(
            Q(number__icontains=query) | Q(name__icontains=query)
        )

    @classmethod
    @transaction.atomic
    def assign_to_workstation(cls, operation: Operation, workstation_id: int):
        """Assign an operation to a workstation."""
        operation.workstations.add(workstation_id)
        return operation

    @classmethod
    @transaction.atomic
    def remove_from_workstation(cls, operation: Operation, workstation_id: int):
        """Remove an operation from a workstation."""
        operation.workstations.remove(workstation_id)
        return operation


class TechnologyOperationComponentService(BaseService):
    """Service for managing technology operation components."""
    model = TechnologyOperationComponent

    @classmethod
    def get_by_technology(cls, technology_id: int):
        """Get all components for a technology."""
        return cls.get_queryset().filter(
            technology_id=technology_id
        ).select_related('operation', 'parent').order_by('node_number')

    @classmethod
    def get_root_components(cls, technology_id: int):
        """Get root components (no parent) for a technology."""
        return cls.get_by_technology(technology_id).filter(parent__isnull=True)

    @classmethod
    @transaction.atomic
    def add_component(
        cls,
        technology_id: int,
        operation_id: int,
        node_number: str,
        parent_id: int = None,
        priority: int = 0,
        **overrides
    ) -> TechnologyOperationComponent:
        """Add a new component to a technology."""
        return cls.model.objects.create(
            technology_id=technology_id,
            operation_id=operation_id,
            node_number=node_number,
            parent_id=parent_id,
            priority=priority,
            **overrides
        )

    @classmethod
    @transaction.atomic
    def reorder_components(cls, technology_id: int, new_order: list) -> int:
        """
        Reorder components based on provided list.

        new_order: list of {'id': int, 'node_number': str, 'priority': int}
        """
        updated = 0
        for item in new_order:
            cls.get_queryset().filter(
                id=item['id'],
                technology_id=technology_id
            ).update(
                node_number=item.get('node_number'),
                priority=item.get('priority', 0)
            )
            updated += 1
        return updated


# Backwards compatibility alias
TechnologyWorkflowService = TechnologyService
