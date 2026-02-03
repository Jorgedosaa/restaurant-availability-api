from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'restaurant', 'reservation_date', 'reservation_time', 'num_people', 'status')
    list_filter = ('restaurant', 'status', 'reservation_date')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información del cliente', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Detalles de la reservación', {
            'fields': ('restaurant', 'reservation_date', 'reservation_time', 'num_people')
        }),
        ('Adicional', {
            'fields': ('special_requests', 'status')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
