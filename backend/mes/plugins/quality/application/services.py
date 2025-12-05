"""
Quality Management Services.

Business logic for quality control, inspections, non-conformance reports,
and statistical process control.
"""
from decimal import Decimal
from django.db import transaction
from django.db.models import Avg, StdDev, Count, Q
from django.utils import timezone

from core.base.services import BaseService, StatefulService
from core.base.exceptions import ValidationException, BusinessRuleException
from ..domain.models import InspectionConfig, QualityCheck, NCR, SPCData


class InspectionConfigService(BaseService):
    """Service for managing inspection configurations."""
    model = InspectionConfig

    @classmethod
    def get_by_operation(cls, operation_id):
        """Get all inspection configs for an operation."""
        return cls.get_queryset().filter(operation_id=operation_id)

    @classmethod
    def get_mandatory_checks(cls, operation_id):
        """Get mandatory inspection configs for an operation."""
        return cls.get_queryset().filter(
            operation_id=operation_id,
            mandatory=True
        )

    @classmethod
    def validate_parameters(cls, check_type: str, parameters: str):
        """
        Validate that parameters are appropriate for the check type.

        For variable checks, parameters should specify tolerance (e.g., "10.0 +/- 0.1")
        For pass_fail checks, parameters are optional descriptions.
        """
        if check_type == 'variable' and not parameters:
            raise ValidationException(
                "Variable checks require parameter specification (e.g., '10.0 +/- 0.1')",
                field='parameters'
            )

    @classmethod
    @transaction.atomic
    def create(cls, **data):
        """Create inspection config with validation."""
        cls.validate_parameters(
            data.get('check_type', ''),
            data.get('parameters', '')
        )
        return super().create(**data)


class QualityCheckService(BaseService):
    """Service for recording and evaluating quality checks."""
    model = QualityCheck

    @classmethod
    def evaluate_result(cls, config: InspectionConfig, result_value: str) -> bool:
        """
        Evaluate if a quality check result passes based on the config.

        For pass_fail: expects "Pass" or "Fail"
        For variable: parses numeric value and compares to tolerance
        """
        if config.check_type == 'pass_fail':
            return result_value.lower() == 'pass'

        # Variable check - parse tolerance from parameters
        # Expected format: "10.0 +/- 0.1" or "10.0 ± 0.1"
        if config.check_type == 'variable':
            try:
                result_num = Decimal(result_value)
                params = config.parameters.replace('±', '+/-')

                if '+/-' in params:
                    parts = params.split('+/-')
                    nominal = Decimal(parts[0].strip())
                    tolerance = Decimal(parts[1].strip())
                    return nominal - tolerance <= result_num <= nominal + tolerance
                else:
                    # No tolerance specified, exact match
                    nominal = Decimal(params.strip())
                    return result_num == nominal
            except (ValueError, InvalidOperation):
                return False

        return False

    @classmethod
    @transaction.atomic
    def record_check(
        cls,
        config: InspectionConfig,
        order_number: str,
        result_value: str,
        inspector_name: str
    ) -> QualityCheck:
        """
        Record a quality check result and auto-evaluate pass/fail.

        If the check fails and is mandatory, may trigger NCR creation.
        """
        passed = cls.evaluate_result(config, result_value)

        check = cls.model.objects.create(
            config=config,
            order_number=order_number,
            result_value=result_value,
            passed=passed,
            inspector_name=inspector_name
        )

        # Auto-create NCR for failed mandatory checks
        if not passed and config.mandatory:
            NCRService.create_from_failed_check(check)

        return check

    @classmethod
    def get_order_checks(cls, order_number: str):
        """Get all quality checks for an order."""
        return cls.get_queryset().filter(
            order_number=order_number
        ).select_related('config', 'config__operation')

    @classmethod
    def get_pass_rate(cls, config_id: int = None, days: int = 30):
        """Calculate pass rate for checks, optionally filtered by config."""
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)

        queryset = cls.get_queryset().filter(timestamp__gte=cutoff)
        if config_id:
            queryset = queryset.filter(config_id=config_id)

        stats = queryset.aggregate(
            total=Count('id'),
            passed=Count('id', filter=Q(passed=True))
        )

        if stats['total'] == 0:
            return None

        return round(stats['passed'] / stats['total'] * 100, 2)


class NCRService(StatefulService):
    """Service for managing Non-Conformance Reports."""
    model = NCR
    state_field = 'status'
    valid_transitions = {
        'quarantine': ['review', 'closed'],
        'review': ['quarantine', 'closed'],
        'closed': [],  # Cannot reopen closed NCRs
    }

    DISPOSITION_CHOICES = ['Rework', 'Scrap', 'Use As Is', 'Return to Supplier']

    @classmethod
    def generate_ncr_number(cls) -> str:
        """Generate unique NCR number."""
        from datetime import date
        today = date.today()
        prefix = f"NCR-{today.strftime('%Y%m%d')}"

        # Find highest existing number for today
        existing = cls.model.objects.filter(
            ncr_number__startswith=prefix
        ).order_by('-ncr_number').first()

        if existing:
            last_seq = int(existing.ncr_number.split('-')[-1])
            return f"{prefix}-{last_seq + 1:04d}"

        return f"{prefix}-0001"

    @classmethod
    @transaction.atomic
    def create_from_failed_check(cls, quality_check: QualityCheck) -> 'NCR':
        """Create NCR automatically from a failed quality check."""
        from mes.plugins.basic.domain.models import Product

        # Get product from the order (this would need order->product relationship)
        # For now, create a generic NCR
        ncr = cls.model.objects.create(
            ncr_number=cls.generate_ncr_number(),
            product_id=quality_check.config.operation.inspection_configs.first().operation.product_id if hasattr(quality_check.config.operation, 'product_id') else None,
            issue_description=f"Failed quality check: {quality_check.config.description}. "
                            f"Result: {quality_check.result_value}",
            status='quarantine'
        )
        return ncr

    @classmethod
    @transaction.atomic
    def create(cls, product_id: int, issue_description: str, **kwargs) -> 'NCR':
        """Create a new NCR with auto-generated number."""
        return cls.model.objects.create(
            ncr_number=cls.generate_ncr_number(),
            product_id=product_id,
            issue_description=issue_description,
            status='quarantine',
            **kwargs
        )

    @classmethod
    def set_disposition(cls, ncr: 'NCR', disposition: str) -> 'NCR':
        """Set the disposition for an NCR."""
        if disposition not in cls.DISPOSITION_CHOICES:
            raise ValidationException(
                f"Invalid disposition. Must be one of: {', '.join(cls.DISPOSITION_CHOICES)}",
                field='disposition'
            )

        ncr.disposition = disposition
        ncr.save(update_fields=['disposition', 'updated_at'])
        return ncr

    @classmethod
    def close(cls, ncr: 'NCR', disposition: str = None) -> 'NCR':
        """Close an NCR with required disposition."""
        if not ncr.disposition and not disposition:
            raise BusinessRuleException(
                'DISPOSITION_REQUIRED',
                'Cannot close NCR without setting disposition'
            )

        if disposition:
            cls.set_disposition(ncr, disposition)

        return cls.change_state(ncr, 'closed')

    @classmethod
    def stats(cls):
        """Get NCR statistics."""
        from core.utils.query_utils import get_stats_aggregation
        return get_stats_aggregation(
            cls.get_queryset(),
            'status',
            cls.model.STATUS_CHOICES
        )


class SPCService(BaseService):
    """Service for Statistical Process Control data and analysis."""
    model = SPCData

    @classmethod
    def record_measurement(
        cls,
        parameter_name: str,
        value: Decimal,
        machine_id: str = ''
    ) -> SPCData:
        """Record a new SPC measurement."""
        return cls.model.objects.create(
            parameter_name=parameter_name,
            value=value,
            machine_id=machine_id
        )

    @classmethod
    def get_parameter_stats(cls, parameter_name: str, limit: int = 100):
        """
        Get statistical analysis for a parameter.

        Returns mean, std dev, min, max, and recent values for control charts.
        """
        queryset = cls.get_queryset().filter(
            parameter_name=parameter_name
        ).order_by('-timestamp')[:limit]

        values = list(queryset.values_list('value', flat=True))

        if not values:
            return None

        from statistics import mean, stdev
        values_float = [float(v) for v in values]

        stats = {
            'parameter_name': parameter_name,
            'count': len(values),
            'mean': mean(values_float),
            'min': min(values_float),
            'max': max(values_float),
        }

        if len(values) > 1:
            stats['std_dev'] = stdev(values_float)
            # Control limits (3-sigma)
            stats['ucl'] = stats['mean'] + 3 * stats['std_dev']
            stats['lcl'] = stats['mean'] - 3 * stats['std_dev']

        return stats

    @classmethod
    def get_control_chart_data(
        cls,
        parameter_name: str,
        limit: int = 50
    ) -> dict:
        """Get data formatted for control chart visualization."""
        queryset = cls.get_queryset().filter(
            parameter_name=parameter_name
        ).order_by('-timestamp')[:limit]

        data_points = list(queryset.values('timestamp', 'value', 'machine_id'))
        data_points.reverse()  # Chronological order

        stats = cls.get_parameter_stats(parameter_name, limit)

        return {
            'parameter_name': parameter_name,
            'data_points': data_points,
            'statistics': stats
        }

    @classmethod
    def check_out_of_control(cls, parameter_name: str, value: Decimal) -> dict:
        """
        Check if a new measurement is out of control limits.

        Returns status and any violations detected.
        """
        stats = cls.get_parameter_stats(parameter_name)

        if not stats or 'ucl' not in stats:
            return {'in_control': True, 'reason': 'Insufficient data'}

        value_float = float(value)
        violations = []

        if value_float > stats['ucl']:
            violations.append(f"Value {value_float} exceeds UCL {stats['ucl']:.4f}")
        if value_float < stats['lcl']:
            violations.append(f"Value {value_float} below LCL {stats['lcl']:.4f}")

        return {
            'in_control': len(violations) == 0,
            'violations': violations,
            'statistics': stats
        }
