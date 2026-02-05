from django.test import TestCase
from datetime import date, time
from availability.models import Restaurant
from reservations.models import Reservation
from availability.engine.capacity import CapacityEngine


class CapacityEngineTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.engine = CapacityEngine()
        self.date = date.today()
        self.time = time(20, 0)

    def test_get_current_occupancy_returns_zero_initially(self):
        """La ocupación inicial debe ser 0."""
        occupancy = self.engine.get_current_occupancy(
            self.restaurant, self.date, self.time
        )
        self.assertEqual(occupancy, 0)

    def test_get_current_occupancy_sums_reservations(self):
        """Debe sumar correctamente las personas de reservas confirmadas y pendientes."""
        Reservation.objects.create(
            restaurant=self.restaurant,
            reservation_date=self.date,
            reservation_time=self.time,
            num_people=4,
            status="confirmed",
        )
        Reservation.objects.create(
            restaurant=self.restaurant,
            reservation_date=self.date,
            reservation_time=self.time,
            num_people=2,
            status="pending",
        )
        # Cancelada no debe contar
        Reservation.objects.create(
            restaurant=self.restaurant,
            reservation_date=self.date,
            reservation_time=self.time,
            num_people=10,
            status="cancelled",
        )

        occupancy = self.engine.get_current_occupancy(
            self.restaurant, self.date, self.time
        )
        self.assertEqual(occupancy, 6)

    def test_check_availability_logic(self):
        """Verifica la lógica booleana de capacidad."""
        # 0 ocupación + 4 solicitados <= 10 max -> True
        self.assertTrue(
            self.engine.check_availability(self.restaurant, self.date, self.time, 4, 10)
        )
        # 0 ocupación + 11 solicitados > 10 max -> False
        self.assertFalse(
            self.engine.check_availability(
                self.restaurant, self.date, self.time, 11, 10
            )
        )
