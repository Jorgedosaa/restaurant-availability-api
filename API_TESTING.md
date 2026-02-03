# Testing de la API - Ejemplos

## Usando cURL

### 1. Crear un Restaurante

```bash
curl -X POST http://localhost:8000/api/availability/restaurants/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "La Bella Italia",
    "description": "Restaurante italiano auténtico",
    "email": "info@bellaitalia.com",
    "phone": "+34 91 234 5678",
    "address": "Calle Mayor 123",
    "city": "Madrid",
    "country": "España",
    "default_capacity": 50
  }'
```

### 2. Crear una Regla de Disponibilidad

```bash
curl -X POST http://localhost:8000/api/availability/availability-rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant": 1,
    "day_of_week": 0,
    "start_time": "11:00:00",
    "end_time": "23:00:00",
    "capacity": 50,
    "is_available": true
  }'
```

### 3. Crear una Temporada

```bash
curl -X POST http://localhost:8000/api/availability/seasons/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant": 1,
    "name": "Verano 2026",
    "start_date": "2026-06-01",
    "end_date": "2026-08-31",
    "capacity_multiplier": 1.2,
    "is_active": true
  }'
```

### 4. Crear una Excepción (Cierre)

```bash
curl -X POST http://localhost:8000/api/availability/exception-dates/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant": 1,
    "date": "2026-12-25",
    "reason": "Navidad - Cierre especial",
    "is_closed": true
  }'
```

### 5. Consultar Disponibilidad por Fecha

```bash
curl http://localhost:8000/api/availability/availability/check_date/ \
  -G --data-urlencode "restaurant_id=1" \
  --data-urlencode "date=2026-02-10"
```

### 6. Verificar Disponibilidad para Horario Específico

```bash
curl -X POST http://localhost:8000/api/availability/availability/check_slot/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 1,
    "date": "2026-02-10",
    "time": "19:30",
    "num_people": 4
  }'
```

### 7. Crear una Reservación

```bash
curl -X POST http://localhost:8000/api/reservations/reservations/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant": 1,
    "customer_name": "Juan García López",
    "customer_email": "juan@example.com",
    "customer_phone": "+34 666 777 888",
    "reservation_date": "2026-02-10",
    "reservation_time": "19:30:00",
    "num_people": 4,
    "special_requests": "Mesa junto a la ventana, sin cebolla"
  }'
```

### 8. Confirmar una Reservación

```bash
curl -X POST http://localhost:8000/api/reservations/reservations/1/confirm/ \
  -H "Content-Type: application/json"
```

### 9. Cancelar una Reservación

```bash
curl -X POST http://localhost:8000/api/reservations/reservations/1/cancel/ \
  -H "Content-Type: application/json"
```

### 10. Obtener mis Reservaciones

```bash
curl http://localhost:8000/api/reservations/reservations/my_reservations/ \
  -G --data-urlencode "email=juan@example.com"
```

## Usando Python requests

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Crear restaurante
response = requests.post(
    f"{BASE_URL}/availability/restaurants/",
    json={
        "name": "Trattoria Roma",
        "email": "info@trattoria.com",
        "phone": "+34 91 234 5678",
        "address": "Paseo de la Castellana 50",
        "city": "Madrid",
        "country": "España",
        "default_capacity": 40
    }
)
restaurant_id = response.json()['id']
print(f"Restaurante creado: {restaurant_id}")

# 2. Crear regla de disponibilidad
response = requests.post(
    f"{BASE_URL}/availability/availability-rules/",
    json={
        "restaurant": restaurant_id,
        "day_of_week": 1,  # Martes
        "start_time": "12:00:00",
        "end_time": "22:30:00",
        "capacity": 40,
        "is_available": True
    }
)
print(f"Regla creada: {response.json()}")

# 3. Consultar disponibilidad
response = requests.get(
    f"{BASE_URL}/availability/availability/check_date/",
    params={
        "restaurant_id": restaurant_id,
        "date": "2026-02-03"
    }
)
print(f"Disponibilidad: {response.json()}")

# 4. Crear reservación
response = requests.post(
    f"{BASE_URL}/reservations/reservations/",
    json={
        "restaurant": restaurant_id,
        "customer_name": "María González",
        "customer_email": "maria@example.com",
        "customer_phone": "+34 666 555 444",
        "reservation_date": "2026-02-03",
        "reservation_time": "20:00:00",
        "num_people": 2,
        "special_requests": "Vegetariano"
    }
)
print(f"Reservación creada: {response.json()}")
```

## Usando Postman

1. Importar colección (crear un nuevo request)
2. Configurar variables de entorno:

   ```
   - base_url: http://localhost:8000/api
   - restaurant_id: 1
   ```

3. Crear requests según los ejemplos anteriores

## Tests Unitarios

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una app específica
python manage.py test availability
python manage.py test reservations

# Con verbose
python manage.py test -v 2

# Con cobertura
coverage run --source='.' manage.py test
coverage report
coverage html  # Generar reporte HTML
```

## Esperados en Tests

✅ Creación de modelos
✅ Validaciones de constraintas únicas
✅ Servicio de disponibilidad
✅ Excepciones y temporadas
✅ Estados de reservaciones
✅ Filtrado de datos
