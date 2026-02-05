from availability.models import Season


class SeasonEngine:
    def __init__(self, model=None):
        self.model = model or Season

    def apply_multiplier(self, restaurant, date_obj, base_capacity):
        season = self.model.objects.filter(
            restaurant=restaurant,
            start_date__lte=date_obj,
            end_date__gte=date_obj,
            is_active=True,
        ).first()

        if season:
            return int(base_capacity * season.capacity_multiplier)

        return base_capacity
