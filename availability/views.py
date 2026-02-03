from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.translation import gettext_lazy as _
from datetime import datetime

from .models import Restaurant, AvailabilityRule, Season, ExceptionDate
from .serializers import (
    RestaurantSerializer,
    AvailabilityRuleSerializer,
    SeasonSerializer,
    ExceptionDateSerializer
)
from .services import AvailabilityService


class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet para Restaurant"""
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]


class AvailabilityRuleViewSet(viewsets.ModelViewSet):
    """ViewSet para AvailabilityRule"""
    queryset = AvailabilityRule.objects.all()
    serializer_class = AvailabilityRuleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant_id', None)
        
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        return queryset


class SeasonViewSet(viewsets.ModelViewSet):
    """ViewSet para Season"""
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant_id', None)
        
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        return queryset


class ExceptionDateViewSet(viewsets.ModelViewSet):
    """ViewSet para ExceptionDate"""
    queryset = ExceptionDate.objects.all()
    serializer_class = ExceptionDateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant_id', None)
        
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        return queryset


class AvailabilityViewSet(viewsets.ViewSet):
    """ViewSet para consultar disponibilidad"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def check_date(self, request):
        """
        Verifica disponibilidad por fecha
        Parámetros query:
        - restaurant_id: ID del restaurante
        - date: Fecha en formato YYYY-MM-DD
        """
        restaurant_id = request.query_params.get('restaurant_id')
        date_str = request.query_params.get('date')

        if not restaurant_id or not date_str:
            return Response(
                {'error': 'restaurant_id y date son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response(
                {'error': 'Restaurante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = AvailabilityService()
        availability = service.get_availability_by_date(restaurant, date)

        return Response({
            'restaurant': restaurant.name,
            'date': date,
            'availability': availability
        })

    @action(detail=False, methods=['post'])
    def check_slot(self, request):
        """
        Verifica disponibilidad para una hora y número de personas específicas
        Body:
        {
            "restaurant_id": 1,
            "date": "2026-02-10",
            "time": "19:30",
            "num_people": 4
        }
        """
        restaurant_id = request.data.get('restaurant_id')
        date_str = request.data.get('date')
        time_str = request.data.get('time')
        num_people = request.data.get('num_people')

        if not all([restaurant_id, date_str, time_str, num_people]):
            return Response(
                {'error': 'Todos los parámetros son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response(
                {'error': 'Restaurante no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha/hora inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = AvailabilityService()
        is_available = service.check_availability(
            restaurant=restaurant,
            date=date,
            time=time,
            num_people=num_people
        )

        return Response({
            'restaurant': restaurant.name,
            'date': date,
            'time': time,
            'num_people': num_people,
            'is_available': is_available
        })
