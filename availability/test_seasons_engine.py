from django.test import TestCase
from datetime import date, timedelta
from availability.models import Restaurant, Season
from availability.engine.seasons import SeasonEngine


class SeasonEngineTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.engine = SeasonEngine()
        self.today = date.today()

    def test_apply_multiplier_returns_base_when_no_season(self):
        """Si no hay temporada, retorna la capacidad base intacta."""
        capacity = self.engine.apply_multiplier(self.restaurant, self.today, 100)
        self.assertEqual(capacity, 100)

    def test_apply_multiplier_applies_active_season(self):
        """Si hay temporada activa, aplica el multiplicador."""
        Season.objects.create(
            restaurant=self.restaurant,
            name="Summer",
            start_date=self.today - timedelta(days=1),
            end_date=self.today + timedelta(days=1),
            capacity_multiplier=1.5,
            is_active=True,
        )
        capacity = self.engine.apply_multiplier(self.restaurant, self.today, 100)
        self.assertEqual(capacity, 150)

    def test_apply_multiplier_ignores_inactive_season(self):
        """Si la temporada está inactiva, la ignora."""
        Season.objects.create(
            restaurant=self.restaurant,
            name="Winter",
            start_date=self.today - timedelta(days=1),
            end_date=self.today + timedelta(days=1),
            capacity_multiplier=0.5,
            is_active=False,
        )
        capacity = self.engine.apply_multiplier(self.restaurant, self.today, 100)
        self.assertEqual(capacity, 100)
