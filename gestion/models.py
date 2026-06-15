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

class PaiementJour(models.Model):

    date = models.DateField(unique=True)

    mobile_money = models.IntegerField(default=0)

    especes = models.IntegerField(default=0)

    def __str__(self):
        return str(self.date)
    
class Activite(models.Model):

    SERVICE_CHOICES = [

        ("impression", "Impression"),
        ("photocopie_bn", "Photocopie Blanc/Noir"),
        ("photocopie_couleur", "Photocopie Couleur"),
        ("inscription", "Inscription"),
        ("traitement_texte", "Traitement de texte"),
        ("creation_cv", "Création CV"),
        ("lettre_motivation", "Lettre de motivation"),
        ("convocation", "Impression convocation"),
        ("paiement", "Paiement"),
        ("confection_document", "Confection document"),
        ("modification_document", "Modification document"),
        ("photo_minute", "Photo minute"),
        ("envoi_document", "Envoi document"),
        ("carte_pvc", "Carte PVC"),
        ("carnet", "Carnet"),
        ("autre", "Autre"),

    ]

    MODE_PAIEMENT_CHOICES = [
        ("mobile_money", "Mobile Money"),
        ("especes", "Espèces"),
    ]

    mode_paiement = models.CharField(
        max_length=20,
        choices=MODE_PAIEMENT_CHOICES,
        default="especes"
    )

    # ================= INFOS CLIENT =================

    client = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    service = models.CharField(
        max_length=50,
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

        if (
            self.montant in [None, 0]
            and self.prix_unitaire > 0
            and self.quantite > 0
        ):
            self.montant = self.prix_unitaire * self.quantite

        super().save(*args, **kwargs)

    # ================= AFFICHAGE =================

    def __str__(self):

        return f"{self.client} - {self.service}"