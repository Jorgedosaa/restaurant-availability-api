from django.test import TestCase
from datetime import date, time
from availability.engine.slots import SlotGenerator


class SlotGeneratorTest(TestCase):
    def setUp(self):
        self.engine = SlotGenerator()
        self.date = date.today()

    def test_generate_slots_creates_correct_intervals(self):
        """Debe generar slots correctos basados en el intervalo."""
        start = time(10, 0)
        end = time(11, 0)
        slots = self.engine.generate_slots(self.date, start, end, interval_minutes=30)

        # Esperamos 10:00 y 10:30. 11:00 es el límite superior (exclusivo en el while loop)
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0], time(10, 0))
        self.assertEqual(slots[1], time(10, 30))

    def test_generate_slots_handles_empty_range(self):
        """Si inicio == fin, no debe generar slots."""
        start = time(10, 0)
        end = time(10, 0)
        slots = self.engine.generate_slots(self.date, start, end)
        self.assertEqual(len(slots), 0)
