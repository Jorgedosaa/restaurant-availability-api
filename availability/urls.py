from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantViewSet,
    AvailabilityRuleViewSet,
    SeasonViewSet,
    ExceptionDateViewSet,
    AvailabilityViewSet
)

# Definición del router para el ViewSet de la app
router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'availability-rules', AvailabilityRuleViewSet, basename='availability-rule')
router.register(r'seasons', SeasonViewSet, basename='season')
router.register(r'exception-dates', ExceptionDateViewSet, basename='exception-date')
router.register(r'availability', AvailabilityViewSet, basename='availability')

app_name = 'availability'

urlpatterns = [
    # Incluye todas las rutas registradas en el router bajo el prefijo base de la app
    path('', include(router.urls)),
]