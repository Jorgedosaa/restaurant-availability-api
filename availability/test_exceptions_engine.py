from django.test import TestCase
from datetime import date
from availability.models import Restaurant, ExceptionDate
from availability.engine.exceptions import ExceptionEngine


class ExceptionEngineTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.engine = ExceptionEngine()
        self.today = date.today()

    def test_get_exception_returns_none_when_no_exception(self):
        """Debe retornar None si no hay excepción para la fecha."""
        result = self.engine.get_exception(self.restaurant, self.today)
        self.assertIsNone(result)

    def test_get_exception_returns_exception_when_exists(self):
        """Debe retornar el objeto ExceptionDate si existe."""
        ExceptionDate.objects.create(
            restaurant=self.restaurant,
            date=self.today,
            reason="Closed for Holiday",
            is_closed=True,
        )

        result = self.engine.get_exception(self.restaurant, self.today)
        self.assertIsNotNone(result)
        self.assertTrue(result.is_closed)
