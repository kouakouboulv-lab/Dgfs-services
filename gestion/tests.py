import csv
import io
from datetime import date, time

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .exports import COLUMNS, safe_cell
from .models import Activite, Depense, PaiementJour


class CSVExportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("responsable", password="test-password")
        self.admin.groups.add(Group.objects.get_or_create(name="admin")[0])
        self.url = reverse("export_csv")

    def read_export(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        content = b"".join(response.streaming_content).decode("utf-8-sig")
        return response, list(csv.DictReader(io.StringIO(content), delimiter=";"))

    def test_anonymous_user_must_log_in(self):
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_ordinary_user_cannot_export(self):
        user = User.objects.create_user("employe")
        self.client.force_login(user)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_superuser_can_export(self):
        user = User.objects.create_superuser("direction", password="test-password")
        self.client.force_login(user)
        self.read_export()

    def test_export_includes_all_dates_and_all_business_fields(self):
        self.client.force_login(self.admin)
        activity = Activite.objects.create(
            date=date(2020, 1, 2), heure=time(9, 30), client="Élodie; SARL",
            service="impression", details='Deux pages\n"Couleur"',
            prix_unitaire=150, quantite=2, montant=300, depense=25,
            mode_paiement="mobile_money", motif="Test",
        )
        Activite.objects.create(date=date(2026, 10, 5), service="autre", montant=500)
        Depense.objects.create(date=date(2020, 1, 2), libelle="Papier", montant=1200, motif=None)
        PaiementJour.objects.create(date=date(2020, 1, 2), mobile_money=300, especes=500)
        self.admin.first_name = "Émile"
        self.admin.email = "responsable@example.com"
        self.admin.save()
        response, rows = self.read_export()
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(rows[0]), COLUMNS)
        exported = next(row for row in rows if row["type"] == "activite" and row["id"] == str(activity.pk))
        for field in Activite._meta.fields:
            self.assertEqual(exported[field.name], str(safe_cell(getattr(activity, field.name))))
        expense = next(row for row in rows if row["type"] == "depense")
        self.assertEqual(expense["montant"], "1200")
        self.assertEqual(expense["motif"], "")
        payment = next(row for row in rows if row["type"] == "paiement_jour")
        self.assertEqual((payment["mobile_money"], payment["especes"]), ("300", "500"))
        user = next(row for row in rows if row["type"] == "utilisateur")
        self.assertEqual(user["prenom"], "Émile")
        self.assertEqual(user["email"], "responsable@example.com")
        self.assertEqual(user["roles"], "admin")
        self.assertNotIn("password", user)
        self.assertTrue(response["Content-Disposition"].endswith('.csv"'))
        self.assertIn("no-store", response["Cache-Control"])

    def test_empty_business_tables_still_have_csv_header(self):
        self.client.force_login(self.admin)
        _, rows = self.read_export()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["type"], "utilisateur")

    def test_formulas_are_escaped_but_numbers_preserved(self):
        for value in ("=1+1", "+SUM(A1)", "-1+2", "@SUM(A1)", "  =1", "\t=1"):
            self.assertEqual(safe_cell(value), "'" + value)
        self.assertEqual(safe_cell(-150), -150)
        self.client.force_login(self.admin)
        Activite.objects.create(client="=1+1", service="autre", montant=100)
        _, rows = self.read_export()
        self.assertEqual(rows[0]["client"], "'=1+1")

    def test_post_not_allowed(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.post(self.url).status_code, 405)
