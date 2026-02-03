from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from datetime import date, time, timedelta
from .models import Restaurant, AvailabilityRule, Season, ExceptionDate
from .services import AvailabilityService
from reservations.models import Reservation

class AvailabilityRuleTestCase(TestCase):
    """Tests para la lógica de disponibilidad y reglas de negocio"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.restaurant = Restaurant.objects.create(
            name='Restaurant Test',
            email='test@restaurant.com',
            phone='123456789',
            address='Test Address',
            city='Test City',
            country='Test Country',
            default_capacity=50
        )
        self.service = AvailabilityService()

        # Helper para obtener el próximo lunes
        today = date.today()
        days_until_monday = (0 - today.weekday()) % 7
        self.monday = today + timedelta(days=days_until_monday)

    def test_create_availability_rule(self):
        """Test básico de creación de modelo"""
        rule = AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(11, 0),
            end_time=time(23, 0),
            capacity=50,
            is_available=True
        )
        self.assertEqual(rule.restaurant, self.restaurant)
        self.assertEqual(rule.capacity, 50)

    def test_availability_service_check_availability(self):
        """Test de flujo positivo: Hay disponibilidad"""
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(11, 0),
            end_time=time(23, 0),
            capacity=50,
            is_available=True
        )
        
        is_available = self.service.check_availability(
            restaurant=self.restaurant,
            date=self.monday,
            time=time(19, 30),
            num_people=4
        )
        self.assertTrue(is_available)

    def test_availability_with_exception_date_closed(self):
        """Test: Las fechas de excepción deben invalidar la disponibilidad"""
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(11, 0),
            end_time=time(23, 0),
            capacity=50,
            is_available=True
        )
        
        ExceptionDate.objects.create(
            restaurant=self.restaurant,
            date=self.monday,
            reason='Cierre especial',
            is_closed=True
        )
        
        is_available = self.service.check_availability(
            restaurant=self.restaurant,
            date=self.monday,
            time=time(19, 30),
            num_people=4
        )
        self.assertFalse(is_available)

    def test_availability_with_season_multiplier(self):
        """
        CORRECCIÓN: Ya no usamos 'get_availability_by_date' (obsoleto).
        Probamos el multiplicador mediante el cálculo de capacidad del servicio.
        """
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(11, 0),
            end_time=time(23, 0),
            capacity=50,
            is_available=True
        )
        
        Season.objects.create(
            restaurant=self.restaurant,
            name='Temporada Alta',
            start_date=self.monday - timedelta(days=1),
            end_date=self.monday + timedelta(days=1),
            capacity_multiplier=2.0, # 50 * 2 = 100
            is_active=True
        )
        
        # Caso 1: Dentro de los 100 de capacidad (Debe ser True)
        is_available = self.service.check_availability(
            restaurant=self.restaurant,
            date=self.monday,
            time=time(12, 0),
            num_people=90
        )
        self.assertTrue(is_available)

        # Caso 2: Supera los 100 de capacidad (Debe ser False)
        is_available = self.service.check_availability(
            restaurant=self.restaurant,
            date=self.monday,
            time=time(12, 0),
            num_people=110
        )
        self.assertFalse(is_available)

    def test_rule_overlap_raises_improperly_configured(self):
        """Test: Validar que el nuevo motor detecta errores de configuración"""
        # Creamos dos reglas que se solapan en el mismo horario
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(12, 0),
            end_time=time(18, 0),
            capacity=50
        )
        AvailabilityRule.objects.create(
            restaurant=self.restaurant,
            day_of_week=0,
            start_time=time(14, 0),
            end_time=time(20, 0),
            capacity=50
        )

        with self.assertRaises(ImproperlyConfigured):
            # El servicio debe explotar al encontrar solapamiento a las 15:00
            self.service.check_availability(
                self.restaurant, self.monday, time(15, 0), 1
            )