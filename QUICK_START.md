# PRIMEROS PASOS - Restaurant Availability

## 1. Configuración inicial

### 1.1 Clonar o descargar el proyecto

```bash
cd /home/george/restaurant_availability
```

### 1.2 Crear archivo .env

```bash
cp .env.example .env
```

Editar `.env` si es necesario (configurar base de datos, idioma, etc.)

### 1.3 Instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar
pip install -r requirements.txt
```

## 2. Base de datos

### 2.1 Migraciones

```bash
python manage.py migrate
```

### 2.2 Crear usuario administrativo

```bash
python manage.py createsuperuser
# Seguir las instrucciones en pantalla
```

### 2.3 Compilar traducciones

```bash
python manage.py compilemessages -l es
python manage.py compilemessages -l en
```

## 3. Ejecutar el servidor

### Opción A: Localmente

```bash
python manage.py runserver
# Acceder a http://localhost:8000
```

### Opción B: Con Docker

```bash
cd docker
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Migrar (si es primera vez)
docker-compose exec web python manage.py migrate
```

## 4. Acceder a la aplicación

### Panel de Administración

- URL: `http://localhost:8000/admin/`
- Usuario: El que creaste en paso 2.2
- Password: La que configuraste

### API REST

- URL: `http://localhost:8000/api/`
- Documentación interactiva disponible en el navegador

## 5. Crear datos de prueba

### 5.1 Vía Admin Django

1. Ir a `/admin/`
2. Crear un Restaurante
3. Crear Reglas de Disponibilidad
4. Crear Temporadas (opcional)
5. Crear Excepciones (opcional)

### 5.2 Vía API (usando cURL o Postman)

Ver archivo `API_TESTING.md` para ejemplos completos.

## 6. Verificar que funciona

```bash
# 1. Listar restaurantes
curl http://localhost:8000/api/availability/restaurants/

# 2. Crear una reservación
curl -X POST http://localhost:8000/api/reservations/reservations/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant": 1,
    "customer_name": "Test User",
    "customer_email": "test@example.com",
    "customer_phone": "123456789",
    "reservation_date": "2026-02-10",
    "reservation_time": "19:30:00",
    "num_people": 2
  }'
```

## 7. Ejecutar tests

```bash
# Todos los tests
python manage.py test

# Solo una app
python manage.py test availability
python manage.py test reservations

# Con detalles
python manage.py test -v 2
```

## 8. Estructura del proyecto

```
restaurant_availability/
├── availability/          # App: Gestión de disponibilidad
├── reservations/          # App: Gestión de reservaciones
├── config/                # Configuración del proyecto
├── docker/                # Docker files
├── locale/                # Traducciones (ES/EN)
├── static/                # Archivos estáticos
├── templates/             # Plantillas HTML
├── manage.py              # CLI de Django
├── requirements.txt       # Dependencias Python
├── README.md              # Documentación principal
└── API_TESTING.md         # Ejemplos de testing
```

## 9. Endpoints principales

### Disponibilidad

- `GET /api/availability/restaurants/` - Listar restaurantes
- `GET /api/availability/availability-rules/` - Listar reglas
- `GET /api/availability/seasons/` - Listar temporadas
- `GET /api/availability/exception-dates/` - Listar excepciones
- `GET /api/availability/availability/check_date/` - Consultar disponibilidad
- `POST /api/availability/availability/check_slot/` - Verificar slot

### Reservaciones

- `GET /api/reservations/reservations/` - Listar reservaciones
- `POST /api/reservations/reservations/` - Crear reservación
- `POST /api/reservations/reservations/{id}/confirm/` - Confirmar
- `POST /api/reservations/reservations/{id}/cancel/` - Cancelar
- `POST /api/reservations/reservations/{id}/complete/` - Completar
- `GET /api/reservations/reservations/my_reservations/` - Mis reservaciones

## 10. Solución de problemas

### Error: "No module named 'django'"

```bash
pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### Error: "Database connection refused"

- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en `.env`
- Alternativamente, usar SQLite en desarrollo

### Migraciones no aplicadas

```bash
python manage.py migrate --fake-initial  # Solo si es necesario
python manage.py migrate
```

### Cambiar idioma

Editar `.env`:

```
LANGUAGE_CODE=es-es  # Español
# o
LANGUAGE_CODE=en-us  # Inglés
```

## 11. Próximos pasos

- [ ] Personalizar estilos y templates
- [ ] Configurar email (para notificaciones)
- [ ] Implementar autenticación avanzada
- [ ] Agregar más validaciones de negocio
- [ ] Crear tests adicionales
- [ ] Documentar endpoints adicionales
- [ ] Configurar CI/CD

## 12. Contacto y Soporte

Para dudas o problemas, revisar:

- `README.md` - Documentación completa
- `API_TESTING.md` - Ejemplos de API
- `CHANGELOG.md` - Histórico de cambios

---

**¡Listo para empezar!** 🚀
