# Restaurant Availability Engine

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14+-red.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Restaurant Availability Engine** es una solución backend de nivel empresarial diseñada para la gestión eficiente y escalable de disponibilidad y reservaciones en tiempo real. Construido sobre **Django** y **Django REST Framework**, este sistema implementa una arquitectura modular avanzada que garantiza flexibilidad, mantenibilidad y alto rendimiento.

El sistema permite a los restaurantes gestionar reglas de operación complejas, incluyendo horarios dinámicos, ajustes por temporada, excepciones de calendario y control de capacidad granular.

---

## 🏗️ Arquitectura y Diseño

El núcleo del sistema se basa en una **Arquitectura Modular** utilizando el patrón **Facade**. El servicio principal, `AvailabilityService`, actúa como un orquestador central que coordina la lógica de negocio a través de motores especializados, asegurando el Principio de Responsabilidad Única (SRP).

### Componentes del Motor

1.  **ExceptionEngine**: Gestiona cierres especiales y capacidades personalizadas por fecha.
2.  **RuleEngine**: Determina las reglas base de operación (días y horarios).
3.  **SeasonEngine**: Aplica multiplicadores de capacidad basados en temporadas (alta/baja).
4.  **CapacityEngine**: Calcula la ocupación en tiempo real y valida contra límites físicos.
5.  **SlotGenerator**: Genera intervalos de tiempo disponibles dinámicamente.

### Flujo de Decisión (Availability Engine)

```mermaid
graph TD
    A[Request: Check Availability] --> B{ExceptionEngine}
    B -- Is Closed? --> C[Return False]
    B -- Has Custom Capacity? --> D[CapacityEngine: Check vs Custom]
    B -- No Exception --> E{RuleEngine}

    E -- No Rule / Not Available --> F[Return False]
    E -- Rule Found --> G[SeasonEngine]

    G -- Apply Multiplier --> H[Calculate Max Capacity]
    H --> I[CapacityEngine: Check vs Calculated]

    D --> J{Is Available?}
    I --> J
    J -- Yes --> K[Return True]
    J -- No --> L[Return False]
```

## 🚀 Quick Start

### 1. Requisitos previos

- Python 3.11+
- Docker y Docker Compose
- PostgreSQL 15+ (si ejecutas localmente)

### 2. Instalación local

```bash
# Clonar repositorio
git clone <repository-url>
cd restaurant_availability

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Compilar mensajes de i18n
python manage.py compilemessages

# Ejecutar servidor
python manage.py runserver
```

### 3. Ejecutar con Docker

```bash
# Levantar servicios
cd docker
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Compilar traducciones
docker-compose exec web python manage.py compilemessages
```

La API estará disponible en `http://localhost:8000`

## 📚 API Endpoints

### Restaurantes

```bash
GET    /api/availability/restaurants/                    # Listar todos
POST   /api/availability/restaurants/                    # Crear
GET    /api/availability/restaurants/{id}/               # Obtener
PUT    /api/availability/restaurants/{id}/               # Actualizar
DELETE /api/availability/restaurants/{id}/               # Eliminar
```

### Reglas de Disponibilidad

```bash
GET    /api/availability/availability-rules/                    # Listar
POST   /api/availability/availability-rules/                    # Crear
GET    /api/availability/availability-rules/{id}/               # Obtener
PUT    /api/availability/availability-rules/{id}/               # Actualizar
DELETE /api/availability/availability-rules/{id}/               # Eliminar

# Filtrar por restaurante
GET    /api/availability/availability-rules/?restaurant_id=1
```

### Temporadas

```bash
GET    /api/availability/seasons/                    # Listar
POST   /api/availability/seasons/                    # Crear
GET    /api/availability/seasons/{id}/               # Obtener
PUT    /api/availability/seasons/{id}/               # Actualizar
DELETE /api/availability/seasons/{id}/               # Eliminar
```

### Fechas de Excepción

```bash
GET    /api/availability/exception-dates/            # Listar
POST   /api/availability/exception-dates/            # Crear
GET    /api/availability/exception-dates/{id}/       # Obtener
PUT    /api/availability/exception-dates/{id}/       # Actualizar
DELETE /api/availability/exception-dates/{id}/       # Eliminar
```

### Disponibilidad (Consultas)

```bash
# Verificar disponibilidad por fecha
GET    /api/availability/availability/check_date/?restaurant_id=1&date=2026-02-10

# Verificar disponibilidad para hora y personas específicas
POST   /api/availability/availability/check_slot/
{
    "restaurant_id": 1,
    "date": "2026-02-10",
    "time": "19:30",
    "num_people": 4
}
```

### Reservaciones

```bash
GET    /api/reservations/reservations/                    # Listar
POST   /api/reservations/reservations/                    # Crear
GET    /api/reservations/reservations/{id}/               # Obtener
PUT    /api/reservations/reservations/{id}/               # Actualizar
DELETE /api/reservations/reservations/{id}/               # Eliminar

# Acciones especiales
POST   /api/reservations/reservations/{id}/confirm/       # Confirmar
POST   /api/reservations/reservations/{id}/cancel/        # Cancelar
POST   /api/reservations/reservations/{id}/complete/      # Completar

# Obtener mis reservaciones
GET    /api/reservations/reservations/my_reservations/?email=cliente@example.com

# Filtros
GET    /api/reservations/reservations/?restaurant_id=1
GET    /api/reservations/reservations/?email=cliente@example.com
GET    /api/reservations/reservations/?status=confirmed
```

## 💾 Estructura de datos

### Restaurant

```json
{
  "id": 1,
  "name": "La Bella Italia",
  "description": "Restaurante italiano tradicional",
  "email": "info@bellaitalia.com",
  "phone": "+34 91 234 5678",
  "address": "Calle Mayor 123",
  "city": "Madrid",
  "country": "España",
  "default_capacity": 50,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-01T10:00:00Z"
}
```

### AvailabilityRule

```json
{
  "id": 1,
  "restaurant": 1,
  "day_of_week": 0,
  "day_of_week_display": "Lunes",
  "start_time": "11:00:00",
  "end_time": "23:00:00",
  "capacity": 50,
  "is_available": true
}
```

### Reservation

```json
{
  "id": 1,
  "restaurant": 1,
  "customer_name": "Juan García",
  "customer_email": "juan@example.com",
  "customer_phone": "+34 666 777 888",
  "reservation_date": "2026-02-10",
  "reservation_time": "19:30:00",
  "num_people": 4,
  "special_requests": "Mesa junto a la ventana",
  "status": "confirmed",
  "status_display": "Confirmada",
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-01T10:00:00Z"
}
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests específicos de una app
python manage.py test availability
python manage.py test reservations

# Con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🌍 Internacionalización

### Soportados idiomas

- **Español (es)**: Traducción completa
- **Inglés (en)**: Traducción completa

### Cambiar idioma

En `config/settings.py`:

```python
LANGUAGE_CODE = 'es-es'  # para español
LANGUAGE_CODE = 'en-us'  # para inglés
```

### Usar traducciones en código

```python
from django.utils.translation import gettext_lazy as _

mensaje = _('Bienvenido')
```

## 📝 Validaciones

### Disponibilidad

- La reserva se permite solo si hay capacidad disponible
- Se respetan excepciones (cierres especiales)
- Se aplican multiplicadores de temporada
- No se permiten dobles bookings que excedan la capacidad

### Reservación

- Email válido requerido
- Mínimo 1 persona
- Validación de disponibilidad automática
- Estados: pending → confirmed → completed/cancelled

## 🔧 Configuración

### Variables de entorno (.env)

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@localhost:5432/restaurant_availability
LANGUAGE_CODE=es-es
TIME_ZONE=America/Mexico_City
```

## 🗺️ Roadmap (Futuras características)

- [ ] Autenticación JWT avanzada
- [ ] Notificaciones por email
- [ ] Sistema de pagos integrado (Stripe/PayPal)
- [ ] Reportes y estadísticas
- [ ] Integración con calendarios externos
- [ ] App móvil (React Native)
- [ ] Métricas de ocupación en tiempo real
- [ ] Sistema de comentarios/reseñas
- [ ] Gestión de mesas por zona
- [ ] Confirmación automática de reservas

## 👥 Buenas prácticas implementadas

✅ Separación de responsabilidades (Models, Serializers, Views, Services)
✅ Validación en capas (Serializers + Services)
✅ Modelos con campos traducibles
✅ Tests unitarios básicos
✅ Documentación API
✅ Estructura modular (apps por contexto)
✅ Manejo de errores apropiado
✅ Índices en BD para optimización
✅ Dockerización completa
✅ Configuración de 12 factores

## 📊 Performance

- Índices en campos de búsqueda frecuente
- Queries optimizadas con select_related/prefetch_related
- Caching compatible (Redis)
- Paginación en endpoints de lista
- Límites de rate limiting (configurables)

## 🔒 Seguridad

- CSRF protection habilitado
- SQL Injection prevención (ORM Django)
- XSS protection
- Validación de entrada en todos los endpoints
- CORS configurado (personalizable)
- Campos de auditoría (created_at, updated_at)

## 📞 Soporte y Contacto

Para reportar bugs o sugerencias, por favor abre un issue en el repositorio.

## 📄 Licencia

MIT License - Ver LICENSE para detalles

---

**Versión**: 1.0.0  
**Última actualización**: 3 de febrero de 2026  
**Autor**: Jorge dos Anjos
