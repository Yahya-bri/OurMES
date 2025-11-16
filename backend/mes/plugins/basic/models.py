"""
Compatibility wrapper that exposes domain models at the historical import path.

Django automatically imports `<app>.models`; keeping this module minimal lets
us move the actual implementations into `domain.models` without breaking the
app registry.
"""

from .domain.models import *  # noqa: F401,F403
