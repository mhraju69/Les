from django.apps import AppConfig


class AirdropConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Airdrop'

    def ready(self):
        import Airdrop.signals
