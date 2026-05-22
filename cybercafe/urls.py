from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),   # ✅ admin fonctionne
    path('', include('gestion.urls')), # ✅ ton app
]