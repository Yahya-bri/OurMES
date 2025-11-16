from django.core.exceptions import ValidationError
from django.db import transaction
from ..domain.models import Technology


class TechnologyWorkflowService:
    """Application layer functions for technology lifecycle management."""

    @staticmethod
    def _validate_state(state: str) -> str:
        valid_states = dict(Technology.STATE_CHOICES)
        if state not in valid_states:
            raise ValidationError(f"Invalid state '{state}'")
        return state

    @classmethod
    def change_state(cls, technology: Technology, new_state: str) -> Technology:
        technology.state = cls._validate_state(new_state)
        technology.save(update_fields=['state', 'updated_at'])
        return technology

    @classmethod
    def bulk_change_state(cls, ids, new_state: str) -> int:
        desired_state = cls._validate_state(new_state)
        with transaction.atomic():
            return Technology.objects.filter(id__in=ids).update(state=desired_state)

    @staticmethod
    def bulk_activate(ids) -> int:
        with transaction.atomic():
            return Technology.objects.filter(id__in=ids).update(active=True)

    @staticmethod
    def bulk_deactivate(ids) -> int:
        with transaction.atomic():
            return Technology.objects.filter(id__in=ids).update(active=False)

    @staticmethod
    def bulk_delete(ids) -> int:
        with transaction.atomic():
            deleted_count, _ = Technology.objects.filter(id__in=ids).delete()
        return deleted_count

    @staticmethod
    def set_master(technology: Technology) -> Technology:
        with transaction.atomic():
            Technology.objects.filter(product=technology.product, master=True).exclude(id=technology.id).update(master=False)
            technology.master = True
            technology.save(update_fields=['master'])
        return technology

    @staticmethod
    def stats():
        total = Technology.objects.count()
        return {
            'total': total,
            'by_state': {
                'draft': Technology.objects.filter(state='draft').count(),
                'accepted': Technology.objects.filter(state='accepted').count(),
                'checked': Technology.objects.filter(state='checked').count(),
                'outdated': Technology.objects.filter(state='outdated').count(),
                'declined': Technology.objects.filter(state='declined').count(),
            },
            'master': Technology.objects.filter(master=True).count(),
            'active': Technology.objects.filter(active=True).count(),
        }
