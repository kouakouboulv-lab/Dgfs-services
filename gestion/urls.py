from django.urls import path
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views

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

    path("api/mise-a-jour-stats/", views.api_mise_a_jour_stats, name="api_stats"),

    # HISTORIQUE
    path("historique/", views.historique, name="historique"),

    # EXPORT PDF
    path("export/pdf/", views.export_pdf, name="export_pdf"),

    path("delete-temp/<int:id>/", views.delete_temp, name="delete_temp"),

    path("statistiques/", views.statistiques, name="statistiques"),
    
    path("set-journal-date/", views.set_journal_date, name="set_journal_date"),
    # SUPPRESSION
    path(
        "supprimer/<int:id>/",
        views.supprimer_activite,
        name="supprimer_activite"
    ),

    path("clear-data/", views.clear_data, name="clear_data"),

    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path("dashboard/users/", views.admin_users, name="admin_users"),
    path("dashboard/users/delete/<int:user_id>/", views.delete_user, name="delete_user"),
    
    
    path("journal-stats/", views.journal_stats, name="journal_stats"),

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