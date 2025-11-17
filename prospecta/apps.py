from django.apps import AppConfig


class ProspectaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prospecta'
    
    def ready(self):
        import prospecta.signals
        import prospecta.oauth_error_patch  # Aplicar patch para capturar erros do Google OAuth
        from django.contrib import admin
        admin.site.site_header = "PROSPECTA - GESTÃO DE OPORTUNIDADES"
        admin.site.site_title = "PROSPECTA"
        admin.site.index_title = "Bem-vindo ao PROSPECTA"
