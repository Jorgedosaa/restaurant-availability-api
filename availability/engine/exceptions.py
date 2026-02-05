from availability.models import ExceptionDate


class ExceptionEngine:
    """
    Motor para gestionar excepciones de disponibilidad.
    Maneja días cerrados o con capacidad personalizada.
    """

    def __init__(self, model=None):
        self.model = model or ExceptionDate

    def get_exception(self, restaurant, date_obj, use_lock=False):
        """
        Busca una excepción para el restaurante y fecha dados.
        Retorna la instancia de ExceptionDate o None.
        """
        queryset = self.model.objects.filter(restaurant=restaurant, date=date_obj)

        if use_lock:
            queryset = queryset.select_for_update()

        return queryset.first()
