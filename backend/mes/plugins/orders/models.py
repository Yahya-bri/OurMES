"""Compatibility wrapper for Django's automatic app loading.

The real model implementations live in `domain.models`, but Django still
imports `<app>.models` when loading the app config. Keeping this file slim
avoids repeating the definitions while letting us grow the layered structure.
"""

from .domain.models import *  # noqa: F401,F403
