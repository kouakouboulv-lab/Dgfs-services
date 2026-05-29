from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from datetime import date, datetime
import calendar
import json

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Activite, Depense



def statistiques(request):

    # ================= DONNEES GLOBALES =================

    activites = Activite.objects.all()
    depenses = Depense.objects.all()

    # ================= KPI =================

    total_revenus = activites.aggregate(
        total=Sum("montant")
    )["total"] or 0

    total_depenses = depenses.aggregate(
        total=Sum("montant")
    )["total"] or 0

    benefice = total_revenus - total_depenses

    nombre_activites = activites.count()

    # ================= GRAPHIQUE GLOBAL =================

    journal = (
        activites
        .values("date")
        .annotate(total=Sum("montant"))
        .order_by("date")
    )

    labels = []
    data = []

    for x in journal:

        if x["date"]:
            labels.append(x["date"].strftime("%d/%m/%Y"))
        else:
            labels.append("Sans date")

        data.append(float(x["total"] or 0))

    # ================= TOP SERVICES =================

    top_services = (
        activites
        .values("service")
        .annotate(total=Sum("montant"))
        .order_by("-total")[:5]
    )

    # ================= HEATMAP GLOBALE =================

    heatmap = []

    for j in range(1, 32):

        total_jour = Activite.objects.filter(
            date__day=j
        ).aggregate(total=Sum("montant"))["total"] or 0

        level = 1

        if total_jour > 50000:
            level = 5

        elif total_jour > 30000:
            level = 4

        elif total_jour > 20000:
            level = 3

        elif total_jour > 10000:
            level = 2

        heatmap.append({

            "jour": j,
            "total": total_jour,
            "level": level

        })

    # ================= PREVISION IA =================

    prediction = int(benefice * 1.1)

    # ================= CONTEXT =================

    context = {

        "total_revenus": total_revenus,

        "total_depenses": total_depenses,

        "benefice": benefice,

        "nombre_activites": nombre_activites,

        "prediction": prediction,

        "labels": json.dumps(labels),

        "data": json.dumps(data),

        "top_services": top_services,

        "heatmap": heatmap,

    }

    return render(
        request,
        "gestion/statistiques.html",
        context
    )

# ================= EXPORT PDF =================
def export_pdf(request):

    # ================= RESPONSE =================
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="journal.pdf"'

    # ================= PDF =================
    p = canvas.Canvas(response, pagesize=A4)

    width, height = A4

    # ================= TITRE =================
    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, height - 50, "JOURNAL CYBERCAFE")

    # ================= DATE =================
    p.setFont("Helvetica", 11)
    p.drawString(40, height - 80, f"Date : {date.today()}")

    # ================= DONNEES =================
    activites = Activite.objects.filter(date=date.today())

    # ================= TABLEAU =================
    data = [
        ["Client", "Service", "Montant", "Date"]
    ]

    total = 0

    for a in activites:
        data.append([
            str(a.client),
            str(a.service),
            f"{a.montant} FCFA",
            a.date.strftime("%d/%m/%Y")
        ])

        total += a.montant

    # Ligne Total
    data.append([
        "",
        "TOTAL",
        f"{total} FCFA",
        ""
    ])

    # ================= STYLE TABLE =================
    table = Table(data, colWidths=[150, 170, 100, 100])

    style = TableStyle([

        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),

        # Alignement
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        # Bordures
        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        # Fond lignes
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),

        # Ligne total
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),

        # Padding
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

    ])

    table.setStyle(style)

    # ================= POSITION =================
    table.wrapOn(p, width, height)
    table.drawOn(p, 30, height - 400)

    # ================= FOOTER =================
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(40, 30, "DGF-SERVICES - Systeme de gestion Cybercafe")

    # ================= SAVE =================
    p.save()

    return response
# ================= LOGIN =================
def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("journal")
        else:
            return render(request, "registration/login.html", {
                "error": "Identifiants incorrects"
            })

    return render(request, "registration/login.html")


# ================= LOGOUT =================
def logout_user(request):
    logout(request)
    return redirect("login")



# ================= MISE A JOUR REGISTRE =================
@login_required

def mise_a_jour_registre(request):

    # ================= SESSION =================

    if "temp_activites" not in request.session:
        request.session["temp_activites"] = []

    if "temp_depenses" not in request.session:
        request.session["temp_depenses"] = []

    # ================= AJOUT ACTIVITE =================

    if request.method == "POST" and "add" in request.POST:

        activites = request.session.get("temp_activites", [])

        prix = int(request.POST.get("prix_unitaire") or 0)
        qte = int(request.POST.get("quantite") or 1)

        # 🔥 garder la date sélectionnée
        request.session["temp_date"] = request.POST.get("date")

        activites.append({

            "id": len(activites),

            "client": request.POST.get("client") or "Inconnu",

            "service": request.POST.get("service"),

            "prix_unitaire": prix,

            "quantite": qte,

            "montant": prix * qte,

        })

        request.session["temp_activites"] = activites
        request.session.modified = True

        return redirect("mise_a_jour_registre")

    # ================= AJOUT DEPENSE =================

    if request.method == "POST" and "add_depense" in request.POST:

        depenses = request.session.get("temp_depenses", [])

        depenses.append({

            "id": len(depenses),

            "montant": int(
                request.POST.get("montant_depense") or 0
            ),

            "motif": request.POST.get("motif") or "",

        })

        request.session["temp_depenses"] = depenses
        request.session.modified = True

        return redirect("mise_a_jour_registre")

    # ================= SAVE FINAL =================

    if request.method == "POST" and "save" in request.POST:

        temp_activites = request.session.get(
            "temp_activites",
            []
        )

        temp_depenses = request.session.get(
            "temp_depenses",
            []
        )

        date_str = request.session.get("temp_date")

        if not date_str:
            return redirect("mise_a_jour_registre")

        try:

            date_obj = datetime.strptime(
                date_str,
                "%Y-%m-%d"
            ).date()

        except:

            date_obj = timezone.now().date()

        # ================= SAVE ACTIVITES =================

        for item in temp_activites:

            Activite.objects.create(

                client=item["client"],

                service=item["service"],

                prix_unitaire=item["prix_unitaire"],

                quantite=item["quantite"],

                montant=item["montant"],

                date=date_obj

            )

        # ================= SAVE DEPENSES =================

        for d in temp_depenses:

            Depense.objects.create(

                montant=d["montant"],

                motif=d["motif"],

                date=date_obj

            )

        # ================= RESET =================

        request.session["temp_activites"] = []

        request.session["temp_depenses"] = []

        request.session["temp_date"] = ""

        request.session.modified = True

        return redirect("mise_a_jour_registre")
    
    # ================= TOTAL CALCUL =================

    session_activites = request.session.get("temp_activites", [])
    session_depenses = request.session.get("temp_depenses", [])

    total_activites = sum(
        int(float(item.get("montant", 0))) for item in session_activites
    )

    total_depenses = sum(
        int(float(item.get("montant", 0))) for item in session_depenses
    )
    
    benefice = total_activites - total_depenses

    if request.method == "POST" and "delete_activite" in request.POST:

        index = int(request.POST.get("id"))

        activites = request.session.get("temp_activites", [])

        if 0 <= index < len(activites):
            activites.pop(index)

        request.session["temp_activites"] = activites
        request.session.modified = True

        return redirect("mise_a_jour_registre")

    if request.method == "POST" and "delete_depense" in request.POST:

        index = int(request.POST.get("id"))

        depenses = request.session.get("temp_depenses", [])

        if 0 <= index < len(depenses):
            depenses.pop(index)

        request.session["temp_depenses"] = depenses
        request.session.modified = True

        return redirect("mise_a_jour_registre")

    # ================= RENDER =================

    return render(request, "gestion/mise_a_jour.html", {

        "session_activites": session_activites,
        "session_depenses": session_depenses,
        "temp_date": request.session.get("temp_date", ""),

        # 🔥 AJOUT IMPORTANT
        "total_activites": total_activites,
        "total_depenses": total_depenses,
        "benefice": benefice,

    })



# ================= JOURNAL =================
@login_required
def journal(request):

    today = timezone.now().date()

    # ================= POST =================
    if request.method == "POST":

        if "save_depense" in request.POST:

            depense = request.POST.get("depense_jour")

            if depense:
                Depense.objects.create(
                    montant=float(depense),
                    date=today
                )

            return redirect("journal")

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

    # ================= DATE SAFE (FIX 500) =================
    selected_date_str = request.GET.get("date")

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except:
        selected_date = today

    # ================= ACTIVITES =================
    activites = Activite.objects.filter(
        date=selected_date
    ).order_by("-id")

    # ================= RECETTES =================
    total = activites.aggregate(
        Sum("montant")
    )["montant__sum"] or 0

    # ================= DEPENSES =================
    total_depenses = Depense.objects.filter(
        date=selected_date
    ).aggregate(
        Sum("montant")
    )["montant__sum"] or 0

    # ================= BENEFICE =================
    benefice = total - total_depenses

    # ================= CALENDRIER =================
    mois = selected_date.month
    annee = selected_date.year

    cal = calendar.monthcalendar(annee, mois)

    calendrier = []

    for week in cal:
        for day in week:
            if day != 0:

                date_obj = datetime(annee, mois, day).date()

                revenu = Activite.objects.filter(
                    date=date_obj
                ).aggregate(Sum("montant"))["montant__sum"] or 0

                depense = Depense.objects.filter(
                    date=date_obj
                ).aggregate(Sum("montant"))["montant__sum"] or 0

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
        "benefice": benefice,
    })


# ================= SUPPRESSION =================
def supprimer_activite(request, id):

    activite = get_object_or_404(Activite, id=id)
    activite.delete()

    return redirect("journal")


# ================= HISTORIQUE =================
@login_required
def historique(request):

    today = timezone.now().date()

    mois = int(request.GET.get("mois", today.month))
    annee = int(request.GET.get("annee", today.year))

    mois = max(1, min(mois, 12))

    activites = Activite.objects.filter(
        date__month=mois,
        date__year=annee
    )

    total_revenu = activites.aggregate(total=Sum("montant"))["total"] or 0

    total_depense = Depense.objects.filter(
        date__month=mois,
        date__year=annee
    ).aggregate(total=Sum("montant"))["total"] or 0

    benefice = total_revenu - total_depense

    total_activites = activites.count()
    moyenne_jour = total_revenu / 30 if total_revenu else 0

    top_clients = activites.values("client").annotate(
        total=Sum("montant")
    ).order_by("-total")[:5]

    if mois == 1:
        prev_month, prev_year = 12, annee - 1
    else:
        prev_month, prev_year = mois - 1, annee

    prev_revenu = Activite.objects.filter(
        date__month=prev_month,
        date__year=prev_year
    ).aggregate(total=Sum("montant"))["total"] or 0

    evolution = ((total_revenu - prev_revenu) / prev_revenu * 100) if prev_revenu else 0

    cal = calendar.monthcalendar(annee, mois)

    calendrier = []
    labels = []
    revenus_chart = []
    depenses_chart = []

    for week in cal:
        for day in week:
            if day != 0:

                date_obj = datetime(annee, mois, day).date()

                revenu = Activite.objects.filter(
                    date=date_obj
                ).aggregate(total=Sum("montant"))["total"] or 0

                depense = Depense.objects.filter(
                    date=date_obj
                ).aggregate(total=Sum("montant"))["total"] or 0

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

    empty_start = range(calendar.monthrange(annee, mois)[0])
    total_cells = len(calendrier) + len(empty_start)
    empty_end = range((7 - total_cells % 7) % 7)

    data_chart = {
        "labels": labels,
        "revenus": revenus_chart,
        "depenses": depenses_chart
    }

    mois_list = [{"value": i, "label": calendar.month_name[i]} for i in range(1, 13)]
    annees_list = list(range(2023, today.year + 1))

    return render(request, "gestion/historique.html", {
        "total_revenu": total_revenu,
        "total_depense": total_depense,
        "benefice": benefice,
        "total_activites": total_activites,
        "moyenne_jour": moyenne_jour,
        "evolution": evolution,
        "top_clients": top_clients,
        "calendrier": calendrier,
        "empty_start": empty_start,
        "empty_end": empty_end,
        "mois": mois,
        "annee": annee,
        "mois_list": mois_list,
        "annees_list": annees_list,
        "data_chart": json.dumps(data_chart),
    })


# ================= DETAILS JOURNAL =================
def journal_details(request):

    date_str = request.GET.get("date")

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

def delete_temp(request, id):

    data = request.session.get("temp_activites", [])

    data = [x for x in data if x["id"] != id]

    request.session["temp_activites"] = data

    return redirect("mise_a_jour_registre")