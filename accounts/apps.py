from django.apps import AppConfig


class CybercafeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cybercafe"

    def ready(self):
        import gestion.signals

class AccountsConfig(AppConfig):
    name = 'accounts'
