from django.db import transaction
from django.db.models import Sum, Q
from django.core.exceptions import ImproperlyConfigured
from .models import AvailabilityRule, Season, ExceptionDate
from reservations.models import Reservation
from datetime import datetime, timedelta, date as date_type

class AvailabilityService:
    """Servicio para validar disponibilidad de reservaciones"""

    def __init__(self, reservation_model=None, rule_model=None, season_model=None, exception_model=None):
        self.reservation_model = reservation_model or Reservation
        self.rule_model = rule_model or AvailabilityRule
        self.season_model = season_model or Season
        self.exception_model = exception_model or ExceptionDate

    def get_availability_by_date(self, restaurant, date_obj):
        """
        Devuelve una lista de horas disponibles para una fecha dada.
        Evita bucles infinitos incrementando el tiempo correctamente.
        """
        # 1. Buscar reglas para ese día (versión simple)
        rule = self.rule_model.objects.filter(
            restaurant=restaurant,
            day_of_week=date_obj.weekday()
        ).first()

        if not rule or not rule.is_available:
            return [] # Cerrado

        # 2. Iterar desde hora inicio a fin cada 15 minutos
        available_slots = []
        
        # Convertimos todo a datetime para poder sumar minutos
        current_dt = datetime.combine(date_obj, rule.start_time)
        end_dt = datetime.combine(date_obj, rule.end_time)
        
        # Intervalo de 15 min
        interval = timedelta(minutes=15)

        # PROTECCIÓN CONTRA BUCLE INFINITO
        safety_counter = 0
        max_loops = 96 # 24 horas * 4 slots = 96

        while current_dt < end_dt:
            time_slot = current_dt.time()
            
            # Verificamos si hay mesa (ej. para 2 personas)
            # Usamos check_availability para validar capacidad real
            if self.check_availability(restaurant, date_obj, time_slot, num_people=2):
                available_slots.append(time_slot)

            # --- LA CLAVE DEL ARREGLO: Avanzar el reloj ---
            current_dt += interval
            
            # Seguridad extra
            safety_counter += 1
            if safety_counter > max_loops:
                break 

        return available_slots

    def check_availability(self, restaurant, date, time, num_people, use_lock=False):
        """ Verifica si hay disponibilidad para una reservación. """
        exceptions = self.exception_model.objects.filter(restaurant=restaurant, date=date)
        
        if use_lock:
            exceptions = exceptions.select_for_update()
            
        exception = exceptions.first()

        if exception:
            if exception.is_closed:
                return False
            if exception.capacity is not None:
                return self._check_capacity(restaurant, date, time, num_people, exception.capacity)

        rule = self._get_availability_rule(restaurant, date, time, use_lock=use_lock)
        if not rule or not rule.is_available:
            return False

        max_capacity = self._get_available_capacity(restaurant, date, rule)
        return self._check_capacity(restaurant, date, time, num_people, max_capacity)

    def _check_capacity(self, restaurant, date, time, num_people, max_capacity):
        existing_pax = self.reservation_model.objects.filter(
            restaurant=restaurant,
            reservation_date=date,
            reservation_time=time,
            status__in=['pending', 'confirmed']
        ).aggregate(total=Sum('num_people'))['total'] or 0

        return (existing_pax + num_people) <= max_capacity

    def _get_availability_rule(self, restaurant, date, time, use_lock=False):
        queryset = self.rule_model.objects.filter(
            restaurant=restaurant,
            day_of_week=date.weekday(),
            start_time__lte=time,
            end_time__gte=time
        )
        if use_lock:
            queryset = queryset.select_for_update()
        rules = list(queryset)
        if not rules: return None
        return rules[0]

    def _get_available_capacity(self, restaurant, date, rule):
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
