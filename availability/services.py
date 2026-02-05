from .models import AvailabilityRule, Season, ExceptionDate
from reservations.models import Reservation

from .engine.exceptions import ExceptionEngine
from .engine.rules import RuleEngine
from .engine.seasons import SeasonEngine
from .engine.capacity import CapacityEngine
from .engine.slots import SlotGenerator


class AvailabilityService:
    """
    Fachada principal del motor de disponibilidad.
    Orquesta la interacción entre los motores:
    - ExceptionEngine
    - RuleEngine
    - SeasonEngine
    - CapacityEngine
    - SlotGenerator
    """

    def __init__(
        self,
        reservation_model=None,
        rule_model=None,
        season_model=None,
        exception_model=None,
    ):
        # Inyección de dependencias (útil para testing)
        self.reservation_model = reservation_model or Reservation
        self.rule_model = rule_model or AvailabilityRule
        self.season_model = season_model or Season
        self.exception_model = exception_model or ExceptionDate

        # Motores especializados
        self.exception_engine = ExceptionEngine(self.exception_model)
        self.rule_engine = RuleEngine(self.rule_model)
        self.season_engine = SeasonEngine(self.season_model)
        self.capacity_engine = CapacityEngine(self.reservation_model)
        self.slot_generator = SlotGenerator()

    def get_availability_by_date(self, restaurant, date_obj):
        """
        Devuelve una lista de slots disponibles para una fecha dada.
        Flujo:
        1. Excepciones
        2. Regla base
        3. Generación de slots
        4. Validación de capacidad por slot
        """
        # 1. Excepción de cierre total
        exception = self.exception_engine.get_exception(restaurant, date_obj)
        if exception and exception.is_closed:
            return []

        # 2. Regla base del día
        rule = self.rule_engine.get_rule(restaurant, date_obj)
        if not rule or not rule.is_available:
            return []

        # 3. Generar slots del día
        time_slots = self.slot_generator.generate_slots(
            date_obj, rule.start_time, rule.end_time
        )

        # 4. Validar capacidad por slot (por defecto 2 personas)
        available_slots = []
        for time_slot in time_slots:
            if self.check_availability(restaurant, date_obj, time_slot, num_people=2):
                available_slots.append(time_slot)

        return available_slots

    def check_availability(self, restaurant, date, time, num_people, use_lock=False):
        """
        Verifica si existe disponibilidad para una reserva específica.
        Flujo:
        1. Excepciones
        2. Reglas
        3. Temporadas
        4. Capacidad real
        """
        # 1. Excepciones
        exception = self.exception_engine.get_exception(
            restaurant, date, use_lock=use_lock
        )
        if exception:
            if exception.is_closed:
                return False

            if exception.capacity is not None:
                return self.capacity_engine.check_availability(
                    restaurant, date, time, num_people, exception.capacity
                )

        # 2. Regla aplicable
        rule = self.rule_engine.get_rule(restaurant, date, time, use_lock=use_lock)
        if not rule or not rule.is_available:
            return False

        # 3. Capacidad ajustada por temporada
        max_capacity = self.season_engine.apply_multiplier(
            restaurant, date, rule.capacity
        )

        # 4. Validación de ocupación
        return self.capacity_engine.check_availability(
            restaurant, date, time, num_people, max_capacity
        )
