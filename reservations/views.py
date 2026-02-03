from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import Reservation
from .serializers import ReservationSerializer
from availability.services import AvailabilityService


class ReservationViewSet(viewsets.ModelViewSet):
    """ViewSet para Reservation"""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por restaurante si se proporciona
        restaurant_id = self.request.query_params.get('restaurant_id', None)
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        
        # Filtrar por email si se proporciona
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(customer_email=email)
        
        # Filtrar por estado si se proporciona
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Crea una nueva reservación"""
        # Instanciamos el servicio aquí (capa de aplicación)
        availability_service = AvailabilityService()
        
        # Iniciamos una transacción atómica para envolver validación y creación
        with transaction.atomic():
            # Pasamos el servicio a través del contexto del serializador
            serializer = self.get_serializer(
                data=request.data,
                context={'availability_service': availability_service}
            )
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirma una reservación"""
        reservation = self.get_object()
        
        if reservation.status != 'pending':
            return Response(
                {'error': 'Solo se pueden confirmar reservaciones pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'confirmed'
        reservation.save()
        
        return Response(
            self.get_serializer(reservation).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancela una reservación"""
        reservation = self.get_object()
        
        if reservation.status == 'completed':
            return Response(
                {'error': 'No se puede cancelar una reservación completada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'cancelled'
        reservation.save()
        
        return Response(
            self.get_serializer(reservation).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marca una reservación como completada"""
        reservation = self.get_object()
        
        if reservation.status != 'confirmed':
            return Response(
                {'error': 'Solo se pueden completar reservaciones confirmadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'completed'
        reservation.save()
        
        return Response(
            self.get_serializer(reservation).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def my_reservations(self, request):
        """Obtiene las reservaciones de un cliente por email"""
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {'error': 'Email es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservations = Reservation.objects.filter(customer_email=email)
        serializer = self.get_serializer(reservations, many=True)
        
        return Response(serializer.data)
