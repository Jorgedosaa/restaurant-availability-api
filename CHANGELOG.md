# CHANGELOG

## [1.0.0] - 2026-02-03

### Agregado

- Modelos Django: Restaurant, AvailabilityRule, Season, ExceptionDate, Reservation
- Serializadores DRF con validación de disponibilidad
- ViewSets con operaciones CRUD completas
- Sistema de validación de disponibilidad en capas (Services + Serializers)
- Endpoints para consultar disponibilidad por fecha y hora
- Acciones especiales para reservaciones (confirm, cancel, complete)
- Tests unitarios para AvailabilityRule y Reservation
- Internacionalización ES/EN (archivos .po)
- Configuración Docker y docker-compose
- Administrador Django personalizado
- Documentación API completa

### Características

- Gestión de múltiples restaurantes
- Reglas de disponibilidad por día de semana
- Temporadas con multiplicadores de capacidad
- Excepciones por fecha (cierres especiales)
- Validación de disponibilidad antes de crear reservas
- Estados de reservación: pending → confirmed → completed/cancelled
- Filtros avanzados en API (restaurante, email, estado)
- Índices de base de datos para optimización
- CORS habilitado

### Seguridad

- Validación en capas
- Protección CSRF
- Inyección SQL prevenida con ORM
- Campos de auditoría (created_at, updated_at)

---

## Roadmap para futuras versiones

### [1.1.0] - Planeado

- [ ] Autenticación JWT
- [ ] Notificaciones por email
- [ ] API GraphQL alternativa
- [ ] Reportes de ocupación

### [1.2.0] - Planeado

- [ ] Integración de pagos
- [ ] Sistema de comentarios
- [ ] Gestión de mesas por zona

### [2.0.0] - Planeado

- [ ] App móvil
- [ ] Integración de calendarios
- [ ] Sistema de promociones
- [ ] Análisis de datos en tiempo real
