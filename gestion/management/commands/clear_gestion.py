from django.core.management.base import BaseCommand
from gestion.models import Depense, PaiementJour, Activite


class Command(BaseCommand):

    help = "Supprime les données de gestion"

    def handle(self, *args, **kwargs):

        Depense.objects.all().delete()
        PaiementJour.objects.all().delete()
        Activite.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS("Données gestion supprimées")
        )