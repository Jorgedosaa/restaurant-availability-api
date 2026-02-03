from django.contrib import admin
from .models import Restaurant, AvailabilityRule, Season, ExceptionDate


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'default_capacity', 'created_at')
    list_filter = ('city', 'country', 'created_at')
    search_fields = ('name', 'email', 'address')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'day_of_week', 'start_time', 'end_time', 'capacity', 'is_available')
    list_filter = ('restaurant', 'day_of_week', 'is_available')
    search_fields = ('restaurant__name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'start_date', 'end_date', 'capacity_multiplier', 'is_active')
    list_filter = ('restaurant', 'is_active', 'start_date')
    search_fields = ('name', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ExceptionDate)
class ExceptionDateAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'date', 'reason', 'is_closed', 'capacity')
    list_filter = ('restaurant', 'date', 'is_closed')
    search_fields = ('reason', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')
