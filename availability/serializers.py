from rest_framework import serializers
from .models import Restaurant, AvailabilityRule, Season, ExceptionDate


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'description', 'email', 'phone',
            'address', 'city', 'country', 'default_capacity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AvailabilityRuleSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True
    )

    class Meta:
        model = AvailabilityRule
        fields = [
            'id', 'restaurant', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'capacity', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = [
            'id', 'restaurant', 'name', 'start_date', 'end_date',
            'capacity_multiplier', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ExceptionDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExceptionDate
        fields = [
            'id', 'restaurant', 'date', 'reason', 'is_closed',
            'capacity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
