from django.urls import path
from django.shortcuts import redirect
from . import views


# ================= HOME =================
def home(request):

    if request.user.is_authenticated:
        return redirect("journal")

    return redirect("login")


# ================= URLS =================
urlpatterns = [

    # HOME
    path("", home, name="home"),

    # JOURNAL
    path("journal/", views.journal, name="journal"),

    # MISE A JOUR REGISTRE
    path(
        "mise-a-jour/",
        views.mise_a_jour_registre,
        name="mise_a_jour_registre"
    ),

    # HISTORIQUE
    path("historique/", views.historique, name="historique"),

    # EXPORT PDF
    path("export/pdf/", views.export_pdf, name="export_pdf"),

    path("delete-temp/<int:id>/", views.delete_temp, name="delete_temp"),

    path("statistiques/", views.statistiques, name="statistiques"),
    
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