from django.apps import AppConfig


class ProspectaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prospecta'

    def ready(self):
        import prospecta.signals
        import prospecta.calendar_signals  # Signals para calendário e documentos
        from django.contrib import admin
        admin.site.site_header = "PROSPECTA - GESTÃO DE OPORTUNIDADES"
        admin.site.site_title = "PROSPECTA"
        admin.site.index_title = "Bem-vindo ao PROSPECTA"
