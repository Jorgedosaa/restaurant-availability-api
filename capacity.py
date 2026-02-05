from django.db.models import Sum
from reservations.models import Reservation


class CapacityEngine:
    def __init__(self, model=None):
        self.model = model or Reservation

    def get_current_occupancy(self, restaurant, date_obj, time_obj):
        # Sumamos personas de reservas confirmadas o pendientes
        result = self.model.objects.filter(
            restaurant=restaurant,
            reservation_date=date_obj,
            reservation_time=time_obj,
            status__in=["confirmed", "pending"],
        ).aggregate(total=Sum("num_people"))

        return result["total"] or 0

    def check_availability(
        self, restaurant, date_obj, time_obj, num_people, max_capacity
    ):
        current_occupancy = self.get_current_occupancy(restaurant, date_obj, time_obj)
        return (current_occupancy + num_people) <= max_capacity
