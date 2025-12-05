"""
Shared validators for OurMES.

Domain-level validators for business rule enforcement.
"""
from django.core.exceptions import ValidationError


def validate_positive(value, field_name='value'):
    """Validate that a value is positive."""
    if value is not None and value <= 0:
        raise ValidationError(f'{field_name} must be positive')


def validate_not_empty(value, field_name='value'):
    """Validate that a value is not empty."""
    if not value:
        raise ValidationError(f'{field_name} cannot be empty')


def validate_state_choice(value, choices, field_name='state'):
    """Validate that a value is in the allowed choices."""
    valid_values = [choice[0] for choice in choices]
    if value not in valid_values:
        raise ValidationError(
            f"Invalid {field_name} '{value}'. Must be one of: {', '.join(valid_values)}"
        )


def validate_date_range(start_date, end_date):
    """Validate that start_date is before end_date."""
    if start_date and end_date and start_date > end_date:
        raise ValidationError('Start date must be before end date')


def validate_quantity(value, min_value=0, max_value=None, field_name='quantity'):
    """Validate quantity is within bounds."""
    if value < min_value:
        raise ValidationError(f'{field_name} must be at least {min_value}')
    if max_value and value > max_value:
        raise ValidationError(f'{field_name} must not exceed {max_value}')
