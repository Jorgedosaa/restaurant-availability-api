from datetime import datetime, timedelta


class SlotGenerator:
    def generate_slots(self, date_obj, start_time, end_time, interval_minutes=15):
        slots = []

        # Combinar fecha y hora para operaciones aritméticas
        current_dt = datetime.combine(date_obj, start_time)
        end_dt = datetime.combine(date_obj, end_time)

        while current_dt < end_dt:
            slots.append(current_dt.time())
            current_dt += timedelta(minutes=interval_minutes)

        return slots
