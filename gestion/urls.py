from django.urls import path
from . import views
from django.shortcuts import redirect

def home(request):
    return redirect("journal")

urlpatterns = [
    path("", home),  # 👈 page d'accueil
    path("journal/", views.journal, name="journal"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("recherche/", views.recherche, name="recherche"),
    path("historique/", views.historique, name="historique"),
    path("export/pdf/", views.export_pdf, name="export_pdf"),
    path('supprimer/<int:id>/', views.supprimer_activite, name='supprimer_activite'),
    path("journal-details/", views.journal_details, name="journal_details")
]

