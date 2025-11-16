from django.apps import AppConfig


def ensure_default_groups():
    """Create default RBAC groups if they don't exist.
    Safe to run multiple times.
    """
    try:
        from django.contrib.auth.models import Group

        for name in ['Operator', 'Planner', 'Supervisor', 'Admin']:
            Group.objects.get_or_create(name=name)
    except Exception:
        # Database not ready or migrations not applied yet
        pass

class SecurityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'security'

    def ready(self):
        ensure_default_groups()