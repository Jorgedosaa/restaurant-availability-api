from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from datetime import time

DAYS_OF_WEEK = [
    (0, _('Lunes')),
    (1, _('Martes')),
    (2, _('Miércoles')),
    (3, _('Jueves')),
    (4, _('Viernes')),
    (5, _('Sábado')),
    (6, _('Domingo')),
]


class Restaurant(models.Model):
    """Modelo de Restaurant"""
    name = models.CharField(max_length=255, verbose_name=_('Nombre'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Descripción'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, verbose_name=_('Teléfono'))
    address = models.CharField(max_length=255, verbose_name=_('Dirección'))
    city = models.CharField(max_length=100, verbose_name=_('Ciudad'))
    country = models.CharField(max_length=100, verbose_name=_('País'))
    default_capacity = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        verbose_name=_('Capacidad por defecto')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Restaurante')
        verbose_name_plural = _('Restaurantes')
        ordering = ['name']

    def __str__(self):
        return self.name


class AvailabilityRule(models.Model):
    """Regla de disponibilidad por día, hora y capacidad"""
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='availability_rules',
        verbose_name=_('Restaurante')
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name=_('Día de la semana')
    )
    start_time = models.TimeField(verbose_name=_('Hora de inicio'))
    end_time = models.TimeField(verbose_name=_('Hora de fin'))
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Capacidad')
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name=_('Disponible')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Regla de disponibilidad')
        verbose_name_plural = _('Reglas de disponibilidad')
        unique_together = [['restaurant', 'day_of_week', 'start_time', 'end_time']]
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Season(models.Model):
    """Temporada con rango de fechas"""
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='seasons',
        verbose_name=_('Restaurante')
    )
    name = models.CharField(max_length=255, verbose_name=_('Nombre'))
    start_date = models.DateField(verbose_name=_('Fecha de inicio'))
    end_date = models.DateField(verbose_name=_('Fecha de fin'))
    capacity_multiplier = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(10.0)],
        verbose_name=_('Multiplicador de capacidad')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Activa'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Temporada')
        verbose_name_plural = _('Temporadas')
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"


class ExceptionDate(models.Model):
    """Fechas especiales de cierre o cambios de disponibilidad"""
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='exception_dates',
        verbose_name=_('Restaurante')
    )
    date = models.DateField(verbose_name=_('Fecha'))
    reason = models.CharField(max_length=255, verbose_name=_('Motivo'))
    is_closed = models.BooleanField(
        default=False,
        verbose_name=_('¿Cerrado?')
    )
    capacity = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name=_('Capacidad especial')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Fecha de excepción')
        verbose_name_plural = _('Fechas de excepción')
        unique_together = [['restaurant', 'date']]
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.reason}"
