from django.db import models
from datetime import date

class Depense(models.Model):
    libelle = models.CharField(max_length=200)
    montant = models.IntegerField()
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

    client = models.CharField(max_length=100)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)

    prix_unitaire = models.IntegerField(default=0)
    quantite = models.IntegerField(default=1)

    montant = models.IntegerField(default=0)

    details = models.TextField(blank=True)

    depense = models.IntegerField(default=0)

    date = models.DateField(default=date.today)
    heure = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 💰 calcul automatique du montant
        self.montant = self.prix_unitaire * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} - {self.service}"