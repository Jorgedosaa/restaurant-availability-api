from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReservationViewSet

router = DefaultRouter()
router.register(r'reservations', ReservationViewSet, basename='reservation')

app_name = 'reservations'

urlpatterns = [
    path('', include(router.urls)),
]
