from availability.models import AvailabilityRule


class RuleEngine:
    def __init__(self, model=None):
        self.model = model or AvailabilityRule

    def get_rule(self, restaurant, date_obj, time_obj=None, use_lock=False):
        # 0=Lunes, 6=Domingo
        day_of_week = date_obj.weekday()

        queryset = self.model.objects.filter(
            restaurant=restaurant, day_of_week=day_of_week, is_available=True
        )

        if time_obj:
            queryset = queryset.filter(start_time__lte=time_obj, end_time__gt=time_obj)

        if use_lock:
            queryset = queryset.select_for_update()

        return queryset.first()
