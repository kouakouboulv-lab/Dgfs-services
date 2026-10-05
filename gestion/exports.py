"""CSV export of persisted application data, excluding authentication secrets."""

import csv

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import Activite, Depense, PaiementJour


COLUMNS = (
    "type", "id", "date", "heure", "client", "service", "details",
    "prix_unitaire", "quantite", "montant", "depense", "mode_paiement",
    "motif", "libelle", "mobile_money", "especes", "nom_utilisateur",
    "prenom", "nom", "email", "actif", "personnel", "superutilisateur",
    "roles", "date_inscription", "derniere_connexion",
)


class CSVBuffer:
    def write(self, value):
        return value


def safe_cell(value):
    if value is None:
        return ""
    # Prevent user-entered text from being interpreted as an Excel formula.
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def export_rows():
    for activity in Activite.objects.order_by("date", "heure", "pk").iterator():
        yield {
            "type": "activite", "id": activity.pk, "date": activity.date,
            "heure": activity.heure, "client": activity.client,
            "service": activity.service, "details": activity.details,
            "prix_unitaire": activity.prix_unitaire, "quantite": activity.quantite,
            "montant": activity.montant, "depense": activity.depense,
            "mode_paiement": activity.mode_paiement, "motif": activity.motif,
        }
    for expense in Depense.objects.order_by("date", "pk").iterator():
        yield {
            "type": "depense", "id": expense.pk, "date": expense.date,
            "libelle": expense.libelle, "montant": expense.montant,
            "motif": expense.motif,
        }
    for payment in PaiementJour.objects.order_by("date", "pk").iterator():
        yield {
            "type": "paiement_jour", "id": payment.pk, "date": payment.date,
            "mobile_money": payment.mobile_money, "especes": payment.especes,
        }
    for user in get_user_model().objects.prefetch_related("groups").order_by("pk").iterator(chunk_size=500):
        yield {
            "type": "utilisateur", "id": user.pk,
            "nom_utilisateur": user.username, "prenom": user.first_name,
            "nom": user.last_name, "email": user.email,
            "actif": user.is_active, "personnel": user.is_staff,
            "superutilisateur": user.is_superuser,
            "roles": ", ".join(sorted(group.name for group in user.groups.all())),
            "date_inscription": user.date_joined,
            "derniere_connexion": user.last_login,
        }


def csv_content():
    writer = csv.writer(CSVBuffer(), delimiter=";", lineterminator="\r\n")
    yield "\ufeff"  # UTF-8 BOM for accented text in Excel.
    yield writer.writerow(COLUMNS)
    for row in export_rows():
        yield writer.writerow([safe_cell(row.get(column)) for column in COLUMNS])


@login_required
@require_GET
def export_csv(request):
    if not (request.user.is_superuser or request.user.groups.filter(name="admin").exists()):
        return HttpResponseForbidden("L’export complet est réservé aux administrateurs.")
    response = StreamingHttpResponse(csv_content(), content_type="text/csv; charset=utf-8")
    filename = timezone.now().strftime("dgf-services-donnees-%Y-%m-%d-%H%M%S.csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Cache-Control"] = "no-store"
    return response
