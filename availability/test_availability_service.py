from django.test import TestCase
from datetime import date, time, timedelta
from availability.models import Restaurant, AvailabilityRule, Season, ExceptionDate
from reservations.models import Reservation
from availability.services import AvailabilityService


class AvailabilityServiceTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Service Restaurant")
        self.service = AvailabilityService()
        # Usamos un lunes futuro para evitar problemas con fechas pasadas
        today = date.today()
        self.monday = today - timedelta(days=today.weekday()) + timedelta(days=7)

    def test_check_availability_returns_false_on_closed_exception(self):
        """Integración: Excepción de cierre bloquea disponibilidad."""
        ExceptionDate.objects.create(
            restaurant=self.restaurant, date=self.monday, is_closed=True
        )
        result = self.service.check_availability(
            self.restaurant, self.monday, time(12, 0), 2
        )
        self.assertFalse(result)

    def test_check_availability_uses_exception_capacity(self):
        """Integración: Excepción con capacidad personalizada anula reglas estándar."""
        ExceptionDate.objects.create(
            restaurant=self.restaurant, date=self.monday, is_closed=False, capacity=5
        )
        # Cabe (5 <= 5)
        self.assertTrue(
            self.service.check_availability(
                self.restaurant, self.monday, time(12, 0), 5
            )
        )
        # No cabe (6 > 5)
        self.assertFalse(
            self.service.check_availability(
                self.restaurant, self.monday, time(12, 0), 6
            )
        )

    def test_check_availability_returns_false_when_no_rule(self):
        """Integración: Sin regla definida retorna False."""
        result = self.service.check_availability(
            self.restaurant, self.monday, time(12, 0), 2
        )
        self.assertFalse(result)

    def test_check_availability_applies_season_multiplier(self):
        """Integración: Regla + Temporada aumenta capacidad."""
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            capacity=10,
        )
        Season.objects.create(
            restaurant=self.restaurant,
            name="Double Capacity",
            start_date=self.monday,
            end_date=self.monday,
            capacity_multiplier=2.0,
            is_active=True,
        )
        # Base 10 * 2 = 20. Solicitud 15 debe pasar.
        self.assertTrue(
            self.service.check_availability(
                self.restaurant, self.monday, time(12, 0), 15
            )
        )

    def test_get_availability_by_date_returns_valid_slots(self):
        """Integración: Flujo completo de generación de slots filtrando ocupados."""
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(10, 0),
            end_time=time(11, 0),  # Genera: 10:00, 10:15, 10:30, 10:45
            capacity=10,
        )

        # Llenamos el slot de las 10:00
        Reservation.objects.create(
            restaurant=self.restaurant,
            reservation_date=self.monday,
            reservation_time=time(10, 0),
            num_people=10,
            status="confirmed",
        )

        slots = self.service.get_availability_by_date(self.restaurant, self.monday)

        self.assertNotIn(time(10, 0), slots)  # Lleno
        self.assertIn(time(10, 15), slots)  # Libre
