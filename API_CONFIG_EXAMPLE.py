# API Settings para la configuración de config/urls.py
# Agregar estas importaciones a config/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/availability/', include('availability.urls')),
    path('api/reservations/', include('reservations.urls')),
]
