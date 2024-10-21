from django.apps import AppConfig


class NginxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.nginx'

    def ready(self):
        import apps.nginx.signals  # Importe o arquivo onde seus signals estão
