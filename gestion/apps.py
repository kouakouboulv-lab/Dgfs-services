from django.apps import AppConfig

class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'

    def ready(self):
        try:
            from django.contrib.auth.models import Group

            Group.objects.get_or_create(name="admin")
            Group.objects.get_or_create(name="user")
        except Exception:
            pass