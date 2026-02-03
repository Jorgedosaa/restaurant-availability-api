from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from availability.models import Restaurant


class Reservation(models.Model):
    """Modelo de Reservación"""
    STATUS_CHOICES = [
        ('pending', _('Pendiente')),
        ('confirmed', _('Confirmada')),
        ('cancelled', _('Cancelada')),
        ('completed', _('Completada')),
    ]

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name=_('Restaurante')
    )
    customer_name = models.CharField(max_length=255, verbose_name=_('Nombre del cliente'))
    customer_email = models.EmailField(verbose_name=_('Email del cliente'))
    customer_phone = models.CharField(max_length=20, verbose_name=_('Teléfono del cliente'))
    reservation_date = models.DateField(verbose_name=_('Fecha de reservación'))
    reservation_time = models.TimeField(verbose_name=_('Hora de reservación'))
    num_people = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Número de personas')
    )
    special_requests = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Solicitudes especiales')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Estado')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Reservación')
        verbose_name_plural = _('Reservaciones')
        ordering = ['reservation_date', 'reservation_time']
        indexes = [
            models.Index(fields=['restaurant', 'reservation_date']),
            models.Index(fields=['customer_email']),
        ]

    def __str__(self):
        return f"{self.customer_name} - {self.reservation_date} {self.reservation_time}"
