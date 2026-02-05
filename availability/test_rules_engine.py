from django.test import TestCase
from datetime import date, time, timedelta
from availability.models import Restaurant, AvailabilityRule
from availability.engine.rules import RuleEngine


class RuleEngineTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.engine = RuleEngine()
        # Calculamos el próximo lunes (0) para consistencia
        today = date.today()
        self.monday = today - timedelta(days=today.weekday()) + timedelta(days=7)

    def test_get_rule_returns_none_when_no_rule(self):
        """Debe retornar None si no hay regla para el día."""
        result = self.engine.get_rule(self.restaurant, self.monday)
        self.assertIsNone(result)

    def test_get_rule_returns_rule_by_day(self):
        """Debe encontrar la regla basada en el día de la semana."""
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,  # Lunes
            start_time=time(9, 0),
            end_time=time(17, 0),
            capacity=10,
        )
        result = self.engine.get_rule(self.restaurant, self.monday)
        self.assertIsNotNone(result)
        self.assertEqual(result.day_of_week, 0)

    def test_get_rule_filters_by_time(self):
        """Debe filtrar reglas que cubran la hora específica si se provee time_obj."""
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
            capacity=10,
        )
        # Hora dentro del rango
        self.assertIsNotNone(
            self.engine.get_rule(self.restaurant, self.monday, time_obj=time(12, 0))
        )
        # Hora fuera del rango
        self.assertIsNone(
            self.engine.get_rule(self.restaurant, self.monday, time_obj=time(18, 0))
        )
