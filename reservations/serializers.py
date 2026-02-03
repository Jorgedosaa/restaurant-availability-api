from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers
from rest_framework.exceptions import APIException
from .models import Reservation
from availability.models import Restaurant
from availability.services import AvailabilityService


class ReservationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Reservation
        fields = [
            'id', 'restaurant', 'customer_name', 'customer_email',
            'customer_phone', 'reservation_date', 'reservation_time',
            'num_people', 'special_requests', 'status', 'status_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']

    def validate(self, data):
        """Valida la disponibilidad de la reservación"""
        restaurant = data.get('restaurant')
        reservation_date = data.get('reservation_date')
        reservation_time = data.get('reservation_time')
        num_people = data.get('num_people')

        # Inyección de Dependencias: Obtenemos el servicio del contexto
        # Esto facilita el testing y permite configurar el servicio desde la vista
        availability_service = self.context.get('availability_service') or AvailabilityService()

        try:
            # Usamos use_lock=True para prevenir Race Conditions (requiere transacción en la vista)
            is_available = availability_service.check_availability(
                restaurant=restaurant,
                date=reservation_date,
                time=reservation_time,
                num_people=num_people,
                use_lock=True
            )
        except ImproperlyConfigured as e:
            # Error crítico de configuración (ej. reglas solapadas): Retornamos 500
            raise APIException(detail=f"Error de configuración del sistema: {str(e)}")

        if not is_available:
            raise serializers.ValidationError(
                "No hay disponibilidad para esta fecha y hora, o el restaurante se encuentra cerrado."
            )

        return data
