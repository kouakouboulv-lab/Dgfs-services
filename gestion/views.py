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
import uuid

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import Activite, Depense, PaiementJour

from .utils.pdf import generer_pdf
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group


# ================= LOGIN =================

def login_user(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔥 CHECK ROLE
            if user.groups.filter(name="admin").exists():
                return redirect("admin_dashboard")

            return redirect("journal")

        else:
            return render(request, "registration/login.html", {
                "error": "Identifiants incorrects"
            })

    return render(request, "registration/login.html")

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not is_admin(request.user):
            return redirect("journal")

        return view_func(request, *args, **kwargs)

    return wrapper


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name="admin").exists()
    )

def is_user(user):
    return user.groups.filter(name="user").exists()


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "dashboard/users.html")



@login_required
@admin_required
@user_passes_test(is_admin)
def admin_users(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        role = request.POST.get("role")

        print("ROLE =", role)  # debug

        if username and password:

            if not User.objects.filter(username=username).exists():

                user = User.objects.create_user(
                    username=username,
                    password=password
                )

                try:
                    group = Group.objects.get(name=role)

                    user.groups.add(group)

                    if role == "admin":
                        user.is_staff = True
                        user.save()

                except Group.DoesNotExist:
                    print("GROUPE INTROUVABLE :", role)
                    user.delete()

        return redirect("admin_users")

    admins = User.objects.filter(groups__name="admin")
    users = User.objects.filter(groups__name="user")

    return render(
        request,
        "dashboard/users.html",
        {
            "admins": admins,
            "users": users,
        }
    )

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()

    return redirect("admin_users")


@login_required
@admin_required
@user_passes_test(is_admin)
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


    # ================= SERVICE VEDETTE =================

    service_vedette_data = (
        activites
        .values("service")
        .annotate(total=Sum("montant"))
        .order_by("-total")
        .first()
    )

    service_vedette = (
        service_vedette_data["service"]
        if service_vedette_data
        else "Aucun"
    )

    # ================= MEILLEUR JOUR =================

    meilleur_jour_data = (
        activites
        .values("date")
        .annotate(total=Sum("montant"))
        .order_by("-total")
        .first()
    )

    meilleur_jour = (
        meilleur_jour_data["date"].strftime("%d/%m/%Y")
        if meilleur_jour_data and meilleur_jour_data["date"]
        else "-"
    )

    # ================= MOYENNE JOURNALIERE =================

    jours_actifs = (
        activites
        .values("date")
        .distinct()
        .count()
    )

    moyenne_jour = (
        int(total_revenus / jours_actifs)
        if jours_actifs > 0
        else 0
    )

    # ================= ACTIVITES RECENTES =================

    activites_recentes = (
        Activite.objects
        .order_by("-date", "-id")[:10]
    )

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
        "service_vedette": service_vedette,
        "meilleur_jour": meilleur_jour,
        "moyenne_jour": moyenne_jour,
        "activites_recentes": activites_recentes,

    }

    return render(
        request,
        "gestion/html/statistiques.html",
        context
    )

# ================= EXPORT PDF ================

def export_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="journal.pdf"'

    width, height = A4

    p = generer_pdf(response, width, height)

    p.showPage()
    p.save()

    return response


# ================= LOGOUT =================
def logout_user(request):
    logout(request)
    return redirect("login")


# ================= DATE UNIQUE =================
def get_date(request):
    date_str = request.session.get("temp_date")

    if not date_str:
        return None  # IMPORTANT : pas de fallback caché

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


# ================= SET DATE =================
def set_journal_date(request):

    if request.method == "POST":

        request.session.flush()

        request.session["temp_date"] = request.POST.get("date")

        request.session["temp_activites"] = []
        request.session["temp_depenses"] = []

    return redirect("mise_a_jour_registre")


# ================= MISE A JOUR REGISTRE =================
def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

@login_required
def mise_a_jour_registre(request):

    # ================= INIT SESSION =================
    if "temp_activites" not in request.session:
        request.session["temp_activites"] = []

    if "temp_depenses" not in request.session:
        request.session["temp_depenses"] = []

    if "temp_date" not in request.session:
        request.session["temp_date"] = ""

    temp_date = request.session.get("temp_date")
    request.session.setdefault("temp_mobile_money", 0)
    request.session.setdefault("temp_especes", 0)

    date_obj = None
    if temp_date:
        try:
            date_obj = datetime.strptime(temp_date, "%Y-%m-%d").date()
        except:
            date_obj = None

    action = request.POST.get("action")

   
    # ================= SAVE PAIEMENT =================
    if request.method == "POST" and action == "save_paiement":

        if not date_obj:
            return JsonResponse({
                "success": False,
                "error": "no_date"
            })

        mobile_money = int(
            request.POST.get("mobile_money") or 0
        )

        especes = int(
            request.POST.get("especes") or 0
        )

        request.session["temp_mobile_money"] = mobile_money
        request.session["temp_especes"] = especes

        request.session.modified = True

        return JsonResponse({
            "success": True,
            "type": "save_paiement"
        })
    # ================= ADD ACTIVITE =================
    if request.method == "POST" and action == "add_activity":

        activites = request.session["temp_activites"]

        prix = int(request.POST.get("prix_unitaire") or 0)
        qte = int(request.POST.get("quantite") or 1)
        
        if not request.session.get("temp_date"):
            return JsonResponse({
                "success": False,
                "error": "no_date"
            }, status=400)
        
        # 🚫 BLOQUAGE PU = 0
        if prix <= 0:
            return JsonResponse({
                "success": False,
                "error": "prix_unitaire_invalid"
            }, status=400)

        item = {
            "id": str(uuid.uuid4()),
            "client": request.POST.get("client") or "Inconnu",
            "service": request.POST.get("service"),
            "prix_unitaire": prix,
            "quantite": qte,
            "montant": prix * qte,
        }

        activites.append(item)
        request.session["temp_activites"] = activites
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "type": "add_activity",
            "data": item
        })


    # ================= ADD DEPENSE =================
    if request.method == "POST" and action == "add_depense":

        depenses = request.session["temp_depenses"]
        if not request.session.get("temp_date"):
            return JsonResponse({
                "success": False,
                "error": "no_date"
            }, status=400)
        
        item = {
            "id": str(uuid.uuid4()),
            "montant": int(request.POST.get("montant_depense") or 0),
            "motif": request.POST.get("motif") or "",
        }

        depenses.append(item)
        request.session["temp_depenses"] = depenses
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "type": "add_depense",
            "data": item
        })
        


    # ================= DELETE ACTIVITE =================
    if request.method == "POST" and action == "delete_activity":

        id_str = request.POST.get("id")

        if not id_str:
            return JsonResponse({
                "success": False,
                "error": "id manquant"
            }, status=400)

        activites = request.session.get("temp_activites", [])

        activites = [
            x for x in activites
            if str(x.get("id")) != str(id_str)
        ]

        request.session["temp_activites"] = activites
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "type": "delete_activity",
            "id": id_str
        })

    # ================= DELETE DEPENSE =================
    if request.method == "POST" and action == "delete_depense":

        id_str = request.POST.get("id")

        if not id_str:
            return JsonResponse({"success": False, "error": "id manquant"}, status=400)

        depenses = request.session.get("temp_depenses", [])

        try:
            depenses = [
                d for d in depenses
                if str(d.get("id")) != str(id_str)
            ]
        except Exception:
            return JsonResponse({"success": False, "error": "erreur suppression"}, status=400)

        request.session["temp_depenses"] = depenses
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "type": "delete_depense",
            "id": id_str
        })
    # ================= SAVE FINAL =================
    if request.method == "POST" and action == "save_final":

        date_str = request.session.get("temp_date")

        if not date_str:
            return JsonResponse({
                "success": False,
                "error": "no_date"
            }, status=400)

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            return JsonResponse({
                "success": False,
                "error": "invalid_date"
            })

        activites = request.session.get("temp_activites", [])
        depenses = request.session.get("temp_depenses", [])

        for item in activites:
            Activite.objects.create(
                client=item["client"],
                service=item["service"],
                prix_unitaire=item["prix_unitaire"],
                quantite=item["quantite"],
                montant=item["montant"],
                date=date_obj
            )

        for d in depenses:
            Depense.objects.create(
                libelle=d.get("motif", ""),
                montant=d.get("montant", 0),
                motif=d.get("motif", ""),
                date=date_obj
            )

        PaiementJour.objects.update_or_create(
            date=date_obj,
            defaults={
                "mobile_money": request.session.get(
                    "temp_mobile_money",
                    0
                ),
                "especes": request.session.get(
                    "temp_especes",
                    0
                ),
            }
        )

        request.session.flush()

        return JsonResponse({
            "success": True,
            "type": "save_final"
        })

   # ================= PAGE HTML (GET NORMAL) =================
    temp_date = request.session.get("temp_date", "")

    # 🔥 SI PAS DE DATE → TOUJOURS VIDE
    if not temp_date:
        session_activites = []
        session_depenses = []
    else:
        session_activites = request.session.get("temp_activites", [])
        session_depenses = request.session.get("temp_depenses", [])

    total_activites = sum(int(x.get("montant", 0) or 0) for x in session_activites)
    total_depenses = sum(int(x.get("montant", 0) or 0) for x in session_depenses)

    benefice = total_activites - total_depenses

    mobile_money = request.session.get(
        "temp_mobile_money",
        0
    )

    especes = request.session.get(
        "temp_especes",
        0
    )

    return render(request, "gestion/html/mise_a_jour.html", {
        "session_activites": session_activites,
        "session_depenses": session_depenses,
        "temp_date": request.session.get("temp_date", ""),

        "total_activites": total_activites,
        "total_depenses": total_depenses,
        "benefice": benefice,

        "mobile_money": mobile_money,
        "especes": especes,
    })

# ================= JOURNAL =================
@login_required
def journal(request):

    today = timezone.now().date()

    # ================= POST =================

    if request.method == "POST":

        action = request.POST.get("action")

        # ================= PAIEMENTS =================

        if action == "save_paiement":

            mobile_money = int(
                request.POST.get("mobile_money") or 0
            )

            especes = int(
                request.POST.get("especes") or 0
            )

            paiement, created = PaiementJour.objects.get_or_create(
                date=today
            )

            paiement.mobile_money = mobile_money
            paiement.especes = especes
            paiement.save()

            return redirect("journal")

        # ================= DEPENSE =================

        elif action == "save_depense":

            depense = request.POST.get("depense_jour")

            if depense:

                Depense.objects.create(
                    montant=float(depense),
                    date=today
                )

            return redirect("journal")

        # ================= ACTIVITE =================

        elif action == "add_activity":

            def safe_float(value, default=0):
                try:
                    if value in [None, "", " "]:
                        return default
                    return float(value)
                except:
                    return default

            client = request.POST.get("client", "").strip()

            # si ton modèle n'accepte pas les valeurs vides
            if not client:
                client = "Sans nom"

            service = request.POST.get("service")

            prix_unitaire = safe_float(
                request.POST.get("prix_unitaire"),
                0
            )

            quantite = safe_float(
                request.POST.get("quantite"),
                0
            )

            montant_total = safe_float(
                request.POST.get("montant_total"),
                0
            )

            # priorité au montant total
            if montant_total > 0:

                montant = montant_total

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

    selected_date_str = request.GET.get("date")

    try:

        selected_date = datetime.strptime(
            selected_date_str,
            "%Y-%m-%d"
        ).date()

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

    cal = calendar.monthcalendar(
        annee,
        mois
    )

    calendrier = []

    for week in cal:

        for day in week:

            if day == 0:
                continue

            date_obj = datetime(
                annee,
                mois,
                day
            ).date()

            revenu = Activite.objects.filter(
                date=date_obj
            ).aggregate(
                Sum("montant")
            )["montant__sum"] or 0

            depense = Depense.objects.filter(
                date=date_obj
            ).aggregate(
                Sum("montant")
            )["montant__sum"] or 0

            calendrier.append({
                "numero": day,
                "date": date_obj,
                "total": revenu,
                "depense": depense,
                "benefice": revenu - depense,
                "is_today": date_obj == today,
                "is_selected": date_obj == selected_date,
            })

    first_weekday = calendar.monthrange(
        annee,
        mois
    )[0]

    empty_start = range(first_weekday)

    total_cells = first_weekday + len(calendrier)

    empty_end = range(
        (7 - total_cells % 7) % 7
    )

    # ================= MOIS =================

    mois_nom = selected_date.strftime("%B")

    # ================= PAIEMENTS =================

    paiement = PaiementJour.objects.filter(
        date=selected_date
    ).first()

    mobile_money = 0
    especes = 0

    if paiement:

        mobile_money = paiement.mobile_money
        especes = paiement.especes

    # ================= TEMPLATE =================

    return render(
        request,
        "gestion/html/journal.html",
        {
            "activites": activites,
            "total": total,
            "total_depenses": total_depenses,
            "benefice": benefice,
            "calendrier": calendrier,
            "empty_start": empty_start,
            "empty_end": empty_end,
            "mois_nom": mois_nom,
            "annee": annee,
            "mobile_money": mobile_money,
            "especes": especes,
        }
    )

# ================= SUPPRESSION =================
def supprimer_activite(request, id):

    activite = get_object_or_404(Activite, id=id)
    activite.delete()

    return redirect("journal")


# ================= HISTORIQUE =================
@login_required
def historique(request):

    today = timezone.now().date()

    date_str = request.GET.get("date")

    if date_str:
        date_selectionnee = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date_selectionnee = today

    mois = int(request.GET.get("mois", date_selectionnee.month))
    annee = int(request.GET.get("annee", date_selectionnee.year))

    mois = max(1, min(mois, 12))

    # Activités du mois sélectionné
    activites = Activite.objects.filter(
        date__month=mois,
        date__year=annee
    )

    total_revenu = (
        activites.aggregate(total=Sum("montant"))["total"]
        or 0
    )

    total_depense = (
        Depense.objects.filter(
            date__month=mois,
            date__year=annee
        ).aggregate(total=Sum("montant"))["total"]
        or 0
    )

    benefice = total_revenu - total_depense

    total_activites = activites.count()

    moyenne_jour = total_revenu / 30 if total_revenu else 0

    paiements = PaiementJour.objects.filter(
        date__month=mois,
        date__year=annee
    )

    total_mobile = paiements.aggregate(
        total=Sum("mobile_money")
    )["total"] or 0

    total_cash = paiements.aggregate(
        total=Sum("especes")
    )["total"] or 0

    top_clients = (
        activites
        .values("client")
        .annotate(total=Sum("montant"))
        .order_by("-total")[:5]
    )

    if mois == 1:
        prev_month = 12
        prev_year = annee - 1
    else:
        prev_month = mois - 1
        prev_year = annee

    prev_revenu = (
        Activite.objects.filter(
            date__month=prev_month,
            date__year=prev_year
        ).aggregate(total=Sum("montant"))["total"]
        or 0
    )

    evolution = (
        ((total_revenu - prev_revenu) / prev_revenu * 100)
        if prev_revenu else 0
    )

    cal = calendar.monthcalendar(annee, mois)

    calendrier = []
    labels = []
    revenus_chart = []
    depenses_chart = []

    for week in cal:
        for day in week:

            if day != 0:

                date_obj = datetime(
                    annee,
                    mois,
                    day
                ).date()

                revenu = (
                    Activite.objects.filter(
                        date=date_obj
                    ).aggregate(total=Sum("montant"))["total"]
                    or 0
                )

                depense = (
                    Depense.objects.filter(
                        date=date_obj
                    ).aggregate(total=Sum("montant"))["total"]
                    or 0
                )

                calendrier.append({
                    "numero": day,
                    "date": date_obj,
                    "revenu": revenu,
                    "depense": depense,
                    "benefice": revenu - depense,
                    "is_today": date_obj == today,
                    "is_selected": date_obj == date_selectionnee,
                })

                labels.append(str(day))
                revenus_chart.append(revenu)
                depenses_chart.append(depense)

    empty_start = range(calendar.monthrange(annee, mois)[0])

    total_cells = len(calendrier) + len(empty_start)

    empty_end = range(
        (7 - total_cells % 7) % 7
    )

    data_chart = {
        "labels": labels,
        "revenus": revenus_chart,
        "depenses": depenses_chart
    }

    mois_list = [
        {
            "value": i,
            "label": calendar.month_name[i]
        }
        for i in range(1, 13)
    ]

    annees_list = list(
        range(2023, today.year + 1)
    )

    return render(
        request,
        "gestion/html/historique.html",
        {
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
            "data_chart": data_chart,
            "total_mobile": total_mobile,
            "total_cash": total_cash,
            "date_selectionnee": date_selectionnee,
        }
    )

def journal_details(request):

    date_str = request.GET.get("date")

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return JsonResponse({
            "activites": [],
            "depenses": [],
            "total_revenu": 0,
            "total_depense": 0,
            "total_mobile": 0,
            "total_cash": 0,
            "benefice": 0
        })

    activites = Activite.objects.filter(date=date_obj)

    data_activites = []
    total_revenu = 0
    total_mobile = 0
    total_cash = 0

    paiement = PaiementJour.objects.filter(
        date=date_obj
    ).first()

    total_mobile = 0
    total_cash = 0

    if paiement:
        total_mobile = paiement.mobile_money
        total_cash = paiement.especes

    for a in activites:
        total_revenu += a.montant

        data_activites.append({
            "client": a.client,
            "service": a.service,
            "montant": a.montant,
        })

    depenses_qs = Depense.objects.filter(date=date_obj)

    data_depenses = []
    total_depense = 0

    for d in depenses_qs:
        total_depense += d.montant

        data_depenses.append({
            "libelle": d.libelle,
            "motif": d.motif,
            "montant": d.montant
        })

    return JsonResponse({
        "activites": data_activites,
        "depenses": data_depenses,
        "total_revenu": total_revenu,
        "total_depense": total_depense,
        "total_mobile": total_mobile,
        "total_cash": total_cash,
        "benefice": total_revenu - total_depense
    })

def delete_temp(request, id):

    data = request.session.get("temp_activites", [])

    data = [x for x in data if x["id"] != id]

    request.session["temp_activites"] = data

    return redirect("mise_a_jour_registre")


def api_dashboard(request):
    mois = int(request.GET.get("mois"))
    annee = int(request.GET.get("annee"))

    activites = Activite.objects.filter(date__month=mois, date__year=annee)

    total_revenu = activites.aggregate(total=Sum("montant"))["total"] or 0
    total_depense = Depense.objects.filter(date__month=mois, date__year=annee).aggregate(total=Sum("montant"))["total"] or 0

    return JsonResponse({
        "kpi": {
            "revenu": total_revenu,
            "depense": total_depense,
            "benefice": total_revenu - total_depense,
        }
    })

def journal_stats(request):

    today = timezone.now().date()

    selected_date_str = request.GET.get("date")

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except:
        selected_date = today

    total = Activite.objects.filter(
        date=selected_date
    ).aggregate(Sum("montant"))["montant__sum"] or 0

    total_depenses = Depense.objects.filter(
        date=selected_date
    ).aggregate(Sum("montant"))["montant__sum"] or 0

    paiement = PaiementJour.objects.filter(
        date=selected_date
    ).first()

    mobile_money = paiement.mobile_money if paiement else 0
    especes = paiement.especes if paiement else 0

    return JsonResponse({
        "total": total,
        "depenses": total_depenses,
        "mobile_money": mobile_money,
        "especes": especes
    })


def api_mise_a_jour_stats(request):

    date_str = request.GET.get("date")

    try:
        datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return JsonResponse({
            "nb_activites": 0,
            "nb_depenses": 0,
            "total_activites": 0,
            "total_depenses": 0,
            "benefice": 0,
            "mobile_money": 0,
            "especes": 0,
            "activites": [],
            "depenses": []
        })

    session_date = request.session.get("temp_date")

    if session_date != date_str:
        session_activites = []
        session_depenses = []
        mobile_money = 0
        especes = 0
    else:
        session_activites = request.session.get("temp_activites", [])
        session_depenses = request.session.get("temp_depenses", [])
        mobile_money = request.session.get("temp_mobile_money", 0)
        especes = request.session.get("temp_especes", 0)

    # =====================
    # COMPTEURS
    # =====================
    nb_activites = len(session_activites)
    nb_depenses = len(session_depenses)

    # =====================
    # MONTANTS
    # =====================
    total_activites = sum(
        float(item.get("montant", 0))
        for item in session_activites
    )

    total_depenses = sum(
        float(item.get("montant", 0))
        for item in session_depenses
    )

    benefice = total_activites - total_depenses

    return JsonResponse({
        # KPI (nombres)
        "nb_activites": nb_activites,
        "nb_depenses": nb_depenses,

        # Totaux financiers
        "total_activites": total_activites,
        "total_depenses": total_depenses,
        "benefice": benefice,

        # Paiements
        "mobile_money": mobile_money,
        "especes": especes,

        # Détails
        "activites": session_activites,
        "depenses": session_depenses,
    })