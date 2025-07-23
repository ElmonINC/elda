from .celery import app as celery_app

# Celery application instance
__all__ = ('celery_app',)