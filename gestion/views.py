from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.utils import timezone

from datetime import date, datetime
import calendar

from reportlab.pdfgen import canvas

from .models import Activite, Depense

from reportlab.pdfgen import canvas
import json


def export_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="journal.pdf"'

    p = canvas.Canvas(response)

    y = 800

    p.drawString(200, 820, "JOURNAL CYBERCAFE")

    activites = Activite.objects.filter(date=date.today())

    for a in activites:

        line = f"{a.client} - {a.service} - {a.montant} FCFA"

        p.drawString(30, y, line)

        y -= 20

        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response

def recherche(request):

    query = request.GET.get("q", "")

    if query:
        resultats = Activite.objects.filter(client__icontains=query)
    else:
        resultats = Activite.objects.none()

    return render(request, "gestion/recherche.html", {
        "resultats": resultats,
        "query": query
    })

def dashboard(request):

    today = date.today()

    activites = Activite.objects.filter(date=today)

    total = activites.aggregate(Sum("montant"))["montant__sum"] or 0
    nb = activites.count()

    return render(request, "gestion/dashboard.html", {
        "total": total,
        "nb": nb
    })

def journal(request):

    today = timezone.now().date()

    # ================= POST =================
    if request.method == "POST":

        # ===== DEPENSE =====
        if "save_depense" in request.POST:

            depense = request.POST.get("depense_jour")

            if depense:
                Depense.objects.create(
                    montant=float(depense),
                    date=today
                )

            return redirect("journal")

        # ===== ACTIVITE =====
        client = request.POST.get("client")
        service = request.POST.get("service")

        def safe_float(value, default=0):
            try:
                if value in [None, "", " "]:
                    return default
                return float(value)
            except:
                return default

        prix_unitaire = safe_float(request.POST.get("prix_unitaire"), 0)
        quantite = safe_float(request.POST.get("quantite"), 1)

        montant_total_raw = request.POST.get("montant_total")

        if montant_total_raw not in [None, "", " "]:
            montant = safe_float(montant_total_raw)
        else:
            montant = prix_unitaire * quantite

        Activite.objects.create(
            client=client,
            service=service,
            prix_unitaire=prix_unitaire,
            quantite=quantite,
            montant=montant,
            date=today
        )

        return redirect("journal")

    # ================= DATE =================
    selected_date = request.GET.get("date")

    if selected_date:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    else:
        selected_date = today

    # ================= ACTIVITES =================
    activites = Activite.objects.filter(date=selected_date).order_by("-id")

    total = activites.aggregate(Sum("montant"))["montant__sum"] or 0

    total_depenses = Depense.objects.filter(date=selected_date).aggregate(
        Sum("montant")
    )["montant__sum"] or 0

    # ================= CALENDRIER =================
    mois = selected_date.month
    annee = selected_date.year

    cal = calendar.monthcalendar(annee, mois)

    calendrier = []

    for week in cal:
        for day in week:
            if day != 0:

                date_obj = datetime(annee, mois, day).date()

                revenu = Activite.objects.filter(date=date_obj).aggregate(
                    Sum("montant")
                )["montant__sum"] or 0

                depense = Depense.objects.filter(date=date_obj).aggregate(
                    Sum("montant")
                )["montant__sum"] or 0

                calendrier.append({
                    "numero": day,
                    "date": date_obj,
                    "total": revenu,
                    "depense": depense,
                    "benefice": revenu - depense,
                    "is_today": date_obj == today,
                    "is_selected": date_obj == selected_date
                })

    first_weekday = calendar.monthrange(annee, mois)[0]
    empty_start = range(first_weekday)

    total_cells = first_weekday + len(calendrier)
    empty_end = range((7 - total_cells % 7) % 7)

    mois_nom = selected_date.strftime("%B")

    return render(request, "gestion/journal.html", {
        "activites": activites,
        "total": total,
        "total_depenses": total_depenses,

        "calendrier": calendrier,
        "empty_start": empty_start,
        "empty_end": empty_end,

        "mois_nom": mois_nom,
        "annee": annee,
    })

def supprimer_activite(request, id):

    activite = get_object_or_404(Activite, id=id)
    activite.delete()

    return redirect("journal")



def historique(request):

    today = timezone.now().date()

    # ================= PARAMS =================
    mois = int(request.GET.get("mois", today.month))
    annee = int(request.GET.get("annee", today.year))

    # sécurité mois
    if mois < 1:
        mois = 1
    if mois > 12:
        mois = 12

    # ================= ACTIVITES (MOIS) =================
    activites = Activite.objects.filter(
        date__month=mois,
        date__year=annee
    )

    total_revenu = activites.aggregate(
        total=Sum("montant")
    )["total"] or 0

    total_depense = Depense.objects.filter(
        date__month=mois,
        date__year=annee
    ).aggregate(
        total=Sum("montant")
    )["total"] or 0

    benefice = total_revenu - total_depense

    # ================= KPI =================
    total_activites = activites.count()
    moyenne_jour = total_revenu / 30 if total_revenu else 0

    # ================= TOP CLIENTS =================
    top_clients = activites.values("client").annotate(
        total=Sum("montant")
    ).order_by("-total")[:5]

    # ================= MOIS PRECEDENT =================
    prev_date = datetime(annee, mois, 1)
    if mois == 1:
        prev_month = 12
        prev_year = annee - 1
    else:
        prev_month = mois - 1
        prev_year = annee

    prev_revenu = Activite.objects.filter(
        date__month=prev_month,
        date__year=prev_year
    ).aggregate(total=Sum("montant"))["total"] or 0

    evolution = 0
    if prev_revenu > 0:
        evolution = ((total_revenu - prev_revenu) / prev_revenu) * 100

    # ================= CALENDRIER =================
    cal = calendar.monthcalendar(annee, mois)

    calendrier = []
    labels = []
    revenus_chart = []
    depenses_chart = []

    for week in cal:
        for day in week:

            if day != 0:

                date_obj = datetime(annee, mois, day).date()

                revenu = Activite.objects.filter(date=date_obj).aggregate(
                    total=Sum("montant")
                )["total"] or 0

                depense = Depense.objects.filter(date=date_obj).aggregate(
                    total=Sum("montant")
                )["total"] or 0

                calendrier.append({
                    "numero": day,
                    "date": date_obj,
                    "revenu": revenu,
                    "depense": depense,
                    "benefice": revenu - depense,
                    "is_today": date_obj == today,
                    "is_selected": False
                })

                labels.append(str(day))
                revenus_chart.append(revenu)
                depenses_chart.append(depense)

    # ================= CALENDRIER ALIGNEMENT =================
    first_weekday = calendar.monthrange(annee, mois)[0]

    empty_start = range(first_weekday)

    total_cells = len(calendrier) + first_weekday
    empty_end = range((7 - (total_cells % 7)) % 7)

    # ================= CHART =================
    data_chart = {
        "labels": labels,
        "revenus": revenus_chart,
        "depenses": depenses_chart
    }

    # ================= MOIS LIST (POUR DROPDOWN HTML) =================
    mois_list = [
        {"value": i, "label": calendar.month_name[i]}
        for i in range(1, 13)
    ]

    # ================= ANNEES LIST =================
    annees_list = list(range(2023, today.year + 1))

    # ================= RETURN =================
    return render(request, "gestion/historique.html", {

        # KPI
        "total_revenu": total_revenu,
        "total_depense": total_depense,
        "benefice": benefice,
        "total_activites": total_activites,
        "moyenne_jour": moyenne_jour,
        "evolution": evolution,
        "top_clients": top_clients,

        # CALENDAR
        "calendrier": calendrier,
        "empty_start": empty_start,
        "empty_end": empty_end,

        # NAVIGATION
        "mois": mois,
        "annee": annee,
        "mois_list": mois_list,
        "annees_list": annees_list,

        # CHART
        "data_chart": json.dumps(data_chart),
    })


def journal_details(request):
    date_str = request.GET.get("date")

    # ⚠️ FIX FORMAT DATE (très important)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return JsonResponse({"activites": [], "total": 0})

    activites = Activite.objects.filter(date=date_obj)

    data = []
    total = 0

    for a in activites:
        total += a.montant
        data.append({
            "client": a.client,
            "service": a.service,
            "montant": a.montant
        })

    return JsonResponse({
        "activites": data,
        "total": total
    })