"""
Domain exceptions for OurMES.

These exceptions represent business rule violations and domain-specific
errors that can occur during application operations.
"""


class DomainException(Exception):
    """
    Base exception for all domain-related errors.

    Use this as the base class for all custom exceptions in the
    application to enable consistent error handling.
    """
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or 'DOMAIN_ERROR'
        super().__init__(self.message)


class ValidationException(DomainException):
    """
    Raised when domain validation fails.

    Use this for business rule validation errors, not for
    input/schema validation which should use serializer validation.
    """
    def __init__(self, message: str, field: str = None):
        self.field = field
        code = f'VALIDATION_ERROR_{field.upper()}' if field else 'VALIDATION_ERROR'
        super().__init__(message, code)


class NotFoundException(DomainException):
    """Raised when a requested entity is not found."""
    def __init__(self, entity: str, identifier=None):
        self.entity = entity
        self.identifier = identifier
        message = f"{entity} not found"
        if identifier:
            message = f"{entity} with id '{identifier}' not found"
        super().__init__(message, 'NOT_FOUND')


class StateTransitionException(DomainException):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, entity: str, current_state: str, target_state: str):
        self.current_state = current_state
        self.target_state = target_state
        message = f"Cannot transition {entity} from '{current_state}' to '{target_state}'"
        super().__init__(message, 'INVALID_STATE_TRANSITION')


class BusinessRuleException(DomainException):
    """Raised when a business rule is violated."""
    def __init__(self, rule: str, message: str):
        self.rule = rule
        super().__init__(message, f'BUSINESS_RULE_{rule.upper()}')


class ConcurrencyException(DomainException):
    """Raised when a concurrent modification conflict is detected."""
    def __init__(self, entity: str):
        message = f"{entity} was modified by another user. Please refresh and try again."
        super().__init__(message, 'CONCURRENCY_CONFLICT')
