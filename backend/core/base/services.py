"""
Base service classes for OurMES.

Services encapsulate business logic and orchestrate domain operations.
All service classes should follow these patterns.
"""
from django.db import transaction
from django.db.models import Model, QuerySet

from .exceptions import NotFoundException, ValidationException


class BaseService:
    """
    Base service class providing common CRUD operations.

    Subclasses should:
    - Define `model` class attribute
    - Override methods to add business logic
    - Use transactions for multi-step operations
    """
    model: Model = None

    @classmethod
    def get_queryset(cls) -> QuerySet:
        """Return the base queryset for this service."""
        return cls.model.objects.all()

    @classmethod
    def get_by_id(cls, id) -> Model:
        """
        Get a single instance by ID.

        Raises:
            NotFoundException: If instance doesn't exist
        """
        try:
            return cls.get_queryset().get(id=id)
        except cls.model.DoesNotExist:
            raise NotFoundException(cls.model.__name__, id)

    @classmethod
    def get_or_none(cls, id) -> Model:
        """Get a single instance by ID or None if not found."""
        try:
            return cls.get_queryset().get(id=id)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    @transaction.atomic
    def create(cls, **data) -> Model:
        """
        Create a new instance.

        Override to add validation and business logic.
        """
        instance = cls.model(**data)
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    @transaction.atomic
    def update(cls, instance: Model, **data) -> Model:
        """
        Update an existing instance.

        Override to add validation and business logic.
        """
        for field, value in data.items():
            setattr(instance, field, value)
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    @transaction.atomic
    def delete(cls, instance: Model) -> None:
        """
        Delete an instance.

        Override to add business rules (e.g., prevent deletion
        of referenced entities).
        """
        instance.delete()

    @classmethod
    @transaction.atomic
    def bulk_create(cls, items: list) -> list:
        """Create multiple instances in a single transaction."""
        instances = [cls.model(**item) for item in items]
        return cls.model.objects.bulk_create(instances)

    @classmethod
    @transaction.atomic
    def bulk_update(cls, ids: list, **data) -> int:
        """Update multiple instances by IDs."""
        return cls.get_queryset().filter(id__in=ids).update(**data)

    @classmethod
    @transaction.atomic
    def bulk_delete(cls, ids: list) -> int:
        """Delete multiple instances by IDs."""
        deleted_count, _ = cls.get_queryset().filter(id__in=ids).delete()
        return deleted_count


class StatefulService(BaseService):
    """
    Base service for entities with state machines.

    Provides state transition validation and tracking.
    Subclasses should define:
    - `state_field`: Name of the state field
    - `valid_transitions`: Dict mapping current state to allowed target states
    """
    state_field: str = 'state'
    valid_transitions: dict = {}

    @classmethod
    def validate_transition(cls, current_state: str, target_state: str) -> bool:
        """Check if a state transition is valid."""
        allowed = cls.valid_transitions.get(current_state, [])
        return target_state in allowed

    @classmethod
    @transaction.atomic
    def change_state(cls, instance: Model, new_state: str, **kwargs) -> Model:
        """
        Change the state of an instance.

        Override to add state change side effects (e.g., audit logging).
        """
        from .exceptions import StateTransitionException

        current_state = getattr(instance, cls.state_field)

        if cls.valid_transitions and not cls.validate_transition(current_state, new_state):
            raise StateTransitionException(
                cls.model.__name__, current_state, new_state
            )

        setattr(instance, cls.state_field, new_state)
        instance.save(update_fields=[cls.state_field, 'updated_at'])
        return instance
