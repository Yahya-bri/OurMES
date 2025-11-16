from django.apps import AppConfig

class ProductionCountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mes.plugins.production_counting'