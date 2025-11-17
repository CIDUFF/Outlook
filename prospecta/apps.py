from django.apps import AppConfig


class ProspectaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prospecta'
    
    def ready(self):
        import prospecta.signals
