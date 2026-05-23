from django.urls import path
from django.shortcuts import redirect
from . import views


# ================= HOME =================
def home(request):

    if request.user.is_authenticated:
        return redirect("journal")

    return redirect("/accounts/login/")


# ================= URLS =================
urlpatterns = [

    # HOME
    path("", home),

    # JOURNAL
    path("journal/", views.journal, name="journal"),

    # DASHBOARD
    path("dashboard/", views.dashboard, name="dashboard"),

    # RECHERCHE
    path("recherche/", views.recherche, name="recherche"),

    # HISTORIQUE
    path("historique/", views.historique, name="historique"),

    # EXPORT PDF
    path("export/pdf/", views.export_pdf, name="export_pdf"),

    # SUPPRESSION
    path(
        "supprimer/<int:id>/",
        views.supprimer_activite,
        name="supprimer_activite"
    ),

    # DETAILS JOURNAL
    path(
        "journal-details/",
        views.journal_details,
        name="journal_details"
    ),

    # LOGIN / LOGOUT
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
]