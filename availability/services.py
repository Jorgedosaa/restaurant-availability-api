from django.db import transaction
from django.db.models import Sum, Q
from django.core.exceptions import ImproperlyConfigured
from .models import AvailabilityRule, Season, ExceptionDate
from reservations.models import Reservation

class AvailabilityService:
    """Servicio para validar disponibilidad de reservaciones"""

    def __init__(self, reservation_model=None, rule_model=None, season_model=None, exception_model=None):
        """
        Inyección de dependencias para facilitar testing.
        Si no se proveen, usa los modelos de Django por defecto.
        """
        self.reservation_model = reservation_model or Reservation
        self.rule_model = rule_model or AvailabilityRule
        self.season_model = season_model or Season
        self.exception_model = exception_model or ExceptionDate

    def check_availability(self, restaurant, date, time, num_people, use_lock=False):
        """
        Verifica si hay disponibilidad para una reservación.
        
        :param use_lock: Si es True, bloquea la regla/excepción (select_for_update) 
                         para prevenir condiciones de carrera. Requiere transaction.atomic().
        """
        # 1. Verificar excepciones (Cierres o capacidades especiales)
        # Optimizacion: Usar filter en lugar de get para evitar Try/Except costoso en flujo normal
        exceptions = self.exception_model.objects.filter(restaurant=restaurant, date=date)
        
        if use_lock:
            exceptions = exceptions.select_for_update()
            
        exception = exceptions.first()

        if exception:
            if exception.is_closed:
                return False
            if exception.capacity is not None:
                # Si hay capacidad especial en la excepción, la usamos como techo
                return self._check_capacity(restaurant, date, time, num_people, exception.capacity)

        # 2. Obtener regla de horario normal
        rule = self._get_availability_rule(restaurant, date, time, use_lock=use_lock)
        if not rule or not rule.is_available:
            return False

        # 3. Calcular capacidad ajustada por temporada
        max_capacity = self._get_available_capacity(restaurant, date, rule)
        
        return self._check_capacity(restaurant, date, time, num_people, max_capacity)

    def _check_capacity(self, restaurant, date, time, num_people, max_capacity):
        """Lógica central de conteo de pax vs capacidad"""
        # NOTA: aggregate() devuelve un diccionario, si es None se convierte a 0
        existing_pax = self.reservation_model.objects.filter(
            restaurant=restaurant,
            reservation_date=date,
            reservation_time=time,
            status__in=['pending', 'confirmed']
        ).aggregate(total=Sum('num_people'))['total'] or 0

        return (existing_pax + num_people) <= max_capacity

    def _get_availability_rule(self, restaurant, date, time, use_lock=False):
        """
        Obtiene la regla de disponibilidad.
        Detecta solapamientos de reglas (Configuration Error).
        """
        queryset = self.rule_model.objects.filter(
            restaurant=restaurant,
            day_of_week=date.weekday(),
            start_time__lte=time,
            end_time__gte=time
        )

        if use_lock:
            queryset = queryset.select_for_update()

        rules = list(queryset) # Evaluamos el queryset

        if not rules:
            return None
        
        if len(rules) > 1:
            # Alerta de solapamiento: El administrador configuró mal los horarios
            raise ImproperlyConfigured(
                f"Conflicto de reglas: Existen {len(rules)} reglas solapadas para {restaurant} el día {date} a las {time}."
            )

        return rules[0]

    def _get_available_capacity(self, restaurant, date, rule):
        """Calcula la capacidad disponible considerando multiplicadores de temporada"""
        capacity = rule.capacity
        season = self.season_model.objects.filter(
            restaurant=restaurant,
            start_date__lte=date,
            end_date__gte=date,
            is_active=True
        ).first()

        if season:
            capacity = int(capacity * season.capacity_multiplier)
        return capacity