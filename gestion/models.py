from django.db import models
from datetime import date
from django.utils import timezone


class Depense(models.Model):

    libelle = models.CharField(max_length=200)

    montant = models.IntegerField()
    
    motif = models.CharField(max_length=255, blank=True, null=True)

    date = models.DateField(default=date.today)

    def __str__(self):
        return self.libelle


class Activite(models.Model):

    SERVICE_CHOICES = [
        ("impression", "Impression"),
        ("inscription", "Inscription"),
        ("photo", "Photo minute"),
        ("carnet", "Carnet"),
        ("autre", "Autre"),
    ]

    # ================= INFOS CLIENT =================

    client = models.CharField(
        max_length=100
    )

    service = models.CharField(
        max_length=20,
        choices=SERVICE_CHOICES
    )

    details = models.TextField(
        blank=True
    )

    # ================= TARIFICATION =================

    prix_unitaire = models.IntegerField(
        default=0
    )

    quantite = models.IntegerField(
        default=1
    )

    montant = models.IntegerField(
        default=0
    )

    # ================= DEPENSE =================

    depense = models.IntegerField(
        default=0
    )

    # ================= DATE & HEURE =================

    # permet d'enregistrer des anciennes activités
    date = models.DateField(
        default=date.today
    )

    # IMPORTANT :
    # auto_now_add=True empêche de choisir l'heure manuellement
    # donc on utilise timezone.now
    heure = models.TimeField(
        default=timezone.now
    )

    # ================= SAVE =================

    def save(self, *args, **kwargs):

        # calcul automatique
        self.montant = self.prix_unitaire * self.quantite

        super().save(*args, **kwargs)

    # ================= AFFICHAGE =================

    def __str__(self):

        return f"{self.client} - {self.service}"