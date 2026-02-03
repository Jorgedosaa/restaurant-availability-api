from django.test import TestCase
from datetime import date, time, timedelta
from unittest.mock import Mock
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import APIException, ValidationError
from availability.models import Restaurant, AvailabilityRule
from .models import Reservation
from .serializers import ReservationSerializer

class ReservationTestCase(TestCase):
    """Tests de integración para el modelo Reservation"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Restaurant Test',
            email='test@restaurant.com',
            phone='123456789',
            address='Test Address',
            city='Test City',
            country='Test Country',
            default_capacity=50
        )

        # Helper para obtener un lunes válido
        today = date.today()
        days_until_monday = (0 - today.weekday()) % 7
        if days_until_monday == 0: days_until_monday = 7
        self.monday = today + timedelta(days=days_until_monday)

    def test_create_reservation(self):
        reservation = Reservation.objects.create(
            restaurant=self.restaurant,
            customer_name='John Doe',
            customer_email='john@example.com',
            customer_phone='123456789',
            reservation_date=self.monday,
            reservation_time=time(19, 30),
            num_people=4,
            status='pending'
        )
        self.assertEqual(reservation.customer_name, 'John Doe')
        self.assertEqual(reservation.num_people, 4)

    def test_multiple_reservations_same_time(self):
        """Verifica que el ORM permita múltiples registros (la lógica de límite la da el servicio)"""
        params = {
            'restaurant': self.restaurant,
            'reservation_date': self.monday,
            'reservation_time': time(19, 30),
            'status': 'confirmed'
        }
        Reservation.objects.create(customer_name='User 1', num_people=4, **params)
        Reservation.objects.create(customer_name='User 2', num_people=3, **params)
        
        count = Reservation.objects.filter(reservation_date=self.monday, reservation_time=time(19, 30)).count()
        self.assertEqual(count, 2)


class ReservationSerializerTestCase(TestCase):
    """Tests unitarios para ReservationSerializer con Mocks de Servicio"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Test Restaurant',
            default_capacity=50
        )
        
        self.valid_data = {
            'restaurant': self.restaurant.id,
            'customer_name': 'Test User',
            'customer_email': 'test@example.com',
            'customer_phone': '123456789',
            'reservation_date': date(2026, 2, 10),
            'reservation_time': time(19, 30),
            'num_people': 4
        }

    def test_validate_success(self):
        """Escenario Exitoso: El servicio confirma disponibilidad"""
        mock_service = Mock()
        mock_service.check_availability.return_value = True