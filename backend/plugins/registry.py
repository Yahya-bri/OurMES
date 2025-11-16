import os
from django.apps import apps


class PluginRegistry:
    """Simple plugin registry with enable/disable filtering via ENV.
    ENV: ENABLED_PLUGINS=basic,orders,technologies (comma separated)
    If unset, all discovered mes.plugins.* are enabled.
    """
    def __init__(self):
        self._plugins = {}
        self._enabled = self._read_enabled()
        self._load_plugins()

    def _read_enabled(self):
        raw = os.getenv('ENABLED_PLUGINS')
        if not raw:
            return None
        return {p.strip() for p in raw.split(',') if p.strip()}

    def _load_plugins(self):
        for app_config in apps.get_app_configs():
            if app_config.name.startswith('mes.plugins.'):
                plugin_name = app_config.name.split('.')[-1]
                if self._enabled is not None and plugin_name not in self._enabled:
                    continue
                self._plugins[plugin_name] = {
                    'name': plugin_name,
                    'label': app_config.label,
                    'models': [model.__name__ for model in app_config.get_models()],
                    'enabled': True,
                }

    def list_plugins(self):
        return list(self._plugins.values())

    def get_plugin(self, name):
        return self._plugins.get(name)