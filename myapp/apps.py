from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        """
        Start APScheduler when Django starts.
        """
        from . import scheduler  # Import scheduler module inside ready() to avoid circular imports
        scheduler.start()
