# DOCUMENTACIÓN DEL SERVICIO DE DISPONIBILIDAD

## Descripción General

El módulo `availability/services.py` contiene la lógica de negocio para validar y consultar disponibilidad de restaurantes. Es el corazón del sistema de reservaciones.

## Clase: AvailabilityService

### Métodos principales

#### 1. `check_availability(restaurant, date, time, num_people)`

Verifica si hay disponibilidad para una reservación específica.

**Parámetros:**

- `restaurant` (Restaurant): Instancia del restaurante
- `date` (date): Fecha de la reservación
- `time` (time): Hora de la reservación
- `num_people` (int): Número de personas

**Retorna:** `bool` - True si hay disponibilidad, False en caso contrario

**Lógica:**

1. Verifica si es una fecha de excepción
2. Si está cerrada, retorna False
3. Si tiene capacidad especial, valida contra esa
4. Obtiene la regla de disponibilidad
5. Calcula capacidad disponible considerando temporadas
6. Cuenta reservaciones existentes
7. Retorna si hay espacio

**Ejemplo:**

```python
from availability.services import AvailabilityService

service = AvailabilityService()
is_available = service.check_availability(
    restaurant=restaurant,
    date=date(2026, 2, 10),
    time=time(19, 30),
    num_people=4
)
```

#### 2. `get_availability_by_date(restaurant, date)`

Obtiene información detallada de disponibilidad para un día completo.

**Parámetros:**

- `restaurant` (Restaurant): Instancia del restaurante
- `date` (date): Fecha a consultar

**Retorna:** `list[dict]` - Lista con disponibilidad por horario

**Estructura de respuesta:**

```python
[
    {
        'time': '11:00:00',
        'available_capacity': 50,
        'reserved_people': 12,
        'remaining_capacity': 38,
        'is_available': True
    },
    {
        'time': '12:00:00',
        'available_capacity': 50,
        'reserved_people': 45,
        'remaining_capacity': 5,
        'is_available': True
    },
    # ...
]
```

**Ejemplo:**

```python
availability = service.get_availability_by_date(
    restaurant=restaurant,
    date=date(2026, 2, 10)
)

for slot in availability:
    print(f"{slot['time']}: {slot['remaining_capacity']} asientos")
```

### Métodos privados (internos)

#### `_is_exception_date(restaurant, date)`

Verifica si una fecha tiene excepcionalidad.

#### `_get_availability_rule(restaurant, date, time)`

Obtiene la regla de disponibilidad para día/hora específicos.

#### `_get_available_capacity(restaurant, date, rule)`

Calcula capacidad disponible considerando temporadas.

## Flujo de Validación

```
┌─────────────────────────────┐
│   check_availability()      │
└──────────┬──────────────────┘
           │
           ├─→ ¿Es fecha de excepción?
           │   │
           │   ├─→ SÍ ¿Está cerrado? → False
           │   │
           │   └─→ Validar contra capacidad especial
           │
           ├─→ Obtener regla de disponibilidad
           │   │
           │   └─→ ¿Regla existe? → False
           │
           ├─→ Calcular capacidad (con temporada)
           │
           ├─→ Contar reservaciones existentes
           │
           └─→ ¿Hay espacio? → True/False
```

## Casos de uso

### Caso 1: Cierre especial

```python
# Crear excepción
ExceptionDate.objects.create(
    restaurant=restaurant,
    date=date(2026, 12, 25),
    reason='Navidad',
    is_closed=True
)

# Verificar
service.check_availability(
    restaurant,
    date(2026, 12, 25),
    time(20, 0),
    4
)  # Retorna: False
```

### Caso 2: Temporada alta con capacidad aumentada

```python
# Crear temporada
Season.objects.create(
    restaurant=restaurant,
    name='Verano',
    start_date=date(2026, 6, 1),
    end_date=date(2026, 8, 31),
    capacity_multiplier=1.5  # 50% más
)

# Regla normal: 50 personas
# En verano: 75 personas
```

### Caso 3: Múltiples reservaciones

```python
# Regla: 50 personas
# Reservación 1: 15 personas (confirmada)
# Reservación 2: 20 personas (confirmada)
# Disponible: 15 personas

# Nueva reservación de 10: OK
# Nueva reservación de 20: FALLA
```

### Caso 4: Capacidad especial en excepción

```python
# Día normal: 50 personas
# Día especial: 30 personas (capacidad reducida)

ExceptionDate.objects.create(
    restaurant=restaurant,
    date=date(2026, 3, 1),
    reason='Mantenimiento parcial',
    is_closed=False,
    capacity=30  # Capacidad especial
)
```

## Integración con Serializers

El `ReservationSerializer` utiliza automáticamente el servicio:

```python
from reservations.serializers import ReservationSerializer

serializer = ReservationSerializer(data={
    "restaurant": 1,
    "customer_name": "Juan",
    "customer_email": "juan@example.com",
    "customer_phone": "123456789",
    "reservation_date": "2026-02-10",
    "reservation_time": "19:30",
    "num_people": 4
})

if serializer.is_valid():
    # Ya fue validada la disponibilidad
    serializer.save()
else:
    print(serializer.errors)
```

## Integración con Vistas

### Endpoint de consulta simple

```python
@action(detail=False, methods=['get'])
def check_date(self, request):
    service = AvailabilityService()
    availability = service.get_availability_by_date(restaurant, date)
    return Response(availability)
```

### Endpoint de verificación puntual

```python
@action(detail=False, methods=['post'])
def check_slot(self, request):
    service = AvailabilityService()
    is_available = service.check_availability(
        restaurant, date, time, num_people
    )
    return Response({'is_available': is_available})
```

## Ejemplos de uso en Tests

```python
def test_availability_with_season(self):
    """Test con temporada activa"""
    # Crear regla: 50 personas
    rule = AvailabilityRule.objects.create(
        restaurant=restaurant,
        day_of_week=0,
        start_time=time(11, 0),
        end_time=time(23, 0),
        capacity=50,
        is_available=True
    )

    # Crear temporada: multiplicar x1.5
    Season.objects.create(
        restaurant=restaurant,
        name='Pico',
        start_date=monday,
        end_date=monday + timedelta(days=30),
        capacity_multiplier=1.5,
        is_active=True
    )

    # Verificar: 50 * 1.5 = 75 personas
    service = AvailabilityService()
    availability = service.get_availability_by_date(restaurant, monday)

    assert availability[0]['available_capacity'] == 75
```

## Performance

### Optimizaciones implementadas

- ✅ Búsqueda directa de excepciones (usando get)
- ✅ Single query para regla de disponibilidad
- ✅ Agregación de reservaciones (Sum)
- ✅ Lógica en Python (no en BD)

### Recomendaciones

- Usar índices en `ExceptionDate.restaurant` y `ExceptionDate.date`
- Cachear resultados de disponibilidad si hay alto tráfico
- Considerar precalcular disponibilidad diariamente

## Extensibilidad

Para agregar nuevas reglas de negocio:

```python
class AvailabilityService:
    def check_availability(self, restaurant, date, time, num_people):
        # Código existente...

        # Nueva regla: no permitir reservas de más de 6 personas
        if num_people > 6:
            return False

        # Resto del código...
```

## Errores comunes

### Error: Rule does not exist

**Causa:** No hay regla para ese día/hora
**Solución:** Crear `AvailabilityRule` para todos los días de operación

### Error: Siempre retorna False

**Causa:** La regla tiene `is_available=False`
**Solución:** Verificar estado de la regla

### Capacidad siempre menor

**Causa:** Temporada activa con multiplicador < 1
**Solución:** Verificar fechas y multiplicador de temporada

---

**Última actualización:** 3 de febrero de 2026
