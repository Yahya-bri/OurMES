"""
Maintenance Management Services.

Business logic for equipment maintenance tracking, preventive maintenance
scheduling, and downtime analysis.
"""
from datetime import timedelta
from django.db import transaction
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone

from core.base.services import BaseService
from core.base.exceptions import ValidationException, BusinessRuleException
from ..domain.models import MaintenanceLog


class MaintenanceService(BaseService):
    """Service for managing maintenance logs and activities."""
    model = MaintenanceLog

    @classmethod
    def get_by_workstation(cls, workstation_id: int):
        """Get all maintenance logs for a workstation."""
        return cls.get_queryset().filter(workstation_id=workstation_id)

    @classmethod
    def get_by_type(cls, maintenance_type: str):
        """Get maintenance logs by type."""
        return cls.get_queryset().filter(type=maintenance_type)

    @classmethod
    def get_active_maintenance(cls):
        """Get ongoing maintenance (no end_time set)."""
        return cls.get_queryset().filter(end_time__isnull=True)

    @classmethod
    def get_recent(cls, days: int = 30):
        """Get maintenance logs from the last N days."""
        cutoff = timezone.now() - timedelta(days=days)
        return cls.get_queryset().filter(start_time__gte=cutoff)

    @classmethod
    @transaction.atomic
    def start_maintenance(
        cls,
        workstation_id: int,
        maintenance_type: str,
        description: str,
        technician_name: str,
        start_time=None
    ) -> MaintenanceLog:
        """
        Start a new maintenance activity.

        Validates that there's no active maintenance for the workstation.
        """
        if maintenance_type not in dict(cls.model.TYPE_CHOICES):
            raise ValidationException(
                f"Invalid maintenance type. Must be one of: {', '.join(dict(cls.model.TYPE_CHOICES).keys())}",
                field='type'
            )

        # Check for active maintenance on this workstation
        active = cls.get_active_maintenance().filter(workstation_id=workstation_id).first()
        if active:
            raise BusinessRuleException(
                'ACTIVE_MAINTENANCE_EXISTS',
                f'Workstation already has active maintenance started at {active.start_time}'
            )

        return cls.model.objects.create(
            workstation_id=workstation_id,
            type=maintenance_type,
            description=description,
            technician_name=technician_name,
            start_time=start_time or timezone.now()
        )

    @classmethod
    @transaction.atomic
    def complete_maintenance(
        cls,
        log: MaintenanceLog,
        end_time=None,
        additional_notes: str = ''
    ) -> MaintenanceLog:
        """Complete a maintenance activity by setting end time."""
        if log.end_time:
            raise BusinessRuleException(
                'MAINTENANCE_ALREADY_COMPLETED',
                'This maintenance log has already been completed'
            )

        end = end_time or timezone.now()
        if end < log.start_time:
            raise ValidationException(
                'End time cannot be before start time',
                field='end_time'
            )

        log.end_time = end
        if additional_notes:
            log.description = f"{log.description}\n\nCompletion notes: {additional_notes}"
        log.save(update_fields=['end_time', 'description', 'updated_at'])
        return log

    @classmethod
    def get_workstation_downtime(cls, workstation_id: int, days: int = 30) -> dict:
        """
        Calculate total downtime for a workstation.

        Returns total hours, breakdown by type, and average duration.
        """
        cutoff = timezone.now() - timedelta(days=days)
        logs = cls.get_by_workstation(workstation_id).filter(
            start_time__gte=cutoff,
            end_time__isnull=False
        )

        # Calculate durations
        total_seconds = 0
        by_type = {}

        for log in logs:
            duration = (log.end_time - log.start_time).total_seconds()
            total_seconds += duration
            by_type[log.type] = by_type.get(log.type, 0) + duration

        total_hours = round(total_seconds / 3600, 2)

        return {
            'workstation_id': workstation_id,
            'period_days': days,
            'total_downtime_hours': total_hours,
            'by_type': {
                mtype: round(seconds / 3600, 2)
                for mtype, seconds in by_type.items()
            },
            'maintenance_count': logs.count(),
            'avg_duration_hours': round(total_hours / logs.count(), 2) if logs.count() > 0 else 0
        }

    @classmethod
    def get_technician_workload(cls, technician_name: str, days: int = 30) -> dict:
        """Get workload statistics for a technician."""
        cutoff = timezone.now() - timedelta(days=days)
        logs = cls.get_queryset().filter(
            technician_name__iexact=technician_name,
            start_time__gte=cutoff
        )

        completed = logs.filter(end_time__isnull=False)
        total_hours = sum(
            (log.end_time - log.start_time).total_seconds() / 3600
            for log in completed
        )

        return {
            'technician': technician_name,
            'period_days': days,
            'total_maintenance_count': logs.count(),
            'completed_count': completed.count(),
            'active_count': logs.filter(end_time__isnull=True).count(),
            'total_hours': round(total_hours, 2)
        }

    @classmethod
    def stats(cls):
        """Get overall maintenance statistics."""
        today = timezone.now().date()
        this_week = timezone.now() - timedelta(days=7)

        return cls.get_queryset().aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(end_time__isnull=True)),
            preventive=Count('id', filter=Q(type='preventive')),
            corrective=Count('id', filter=Q(type='corrective')),
            breakdown=Count('id', filter=Q(type='breakdown')),
            this_week=Count('id', filter=Q(start_time__gte=this_week)),
            today=Count('id', filter=Q(start_time__date=today)),
        )

    @classmethod
    def get_breakdown_frequency(cls, workstation_id: int = None, days: int = 90) -> list:
        """
        Analyze breakdown frequency for predictive maintenance insights.

        Returns list of workstations with their breakdown counts.
        """
        cutoff = timezone.now() - timedelta(days=days)
        queryset = cls.get_queryset().filter(
            type='breakdown',
            start_time__gte=cutoff
        )

        if workstation_id:
            queryset = queryset.filter(workstation_id=workstation_id)

        return list(
            queryset.values('workstation__number', 'workstation__name')
            .annotate(breakdown_count=Count('id'))
            .order_by('-breakdown_count')
        )
