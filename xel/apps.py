from django.apps import AppConfig


class XelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xel'

    def ready(self):
        import xel.signals  # Import signals