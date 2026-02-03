#!/usr/bin/env bash
set -euo pipefail

# Activar entorno virtual si existe
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

export DJANGO_SETTINGS_MODULE=config.settings

echo "Ejecutando migraciones Django..."
python manage.py migrate --noinput

echo "Eliminando ContentType para evitar duplicados al cargar fixtures..."
python manage.py shell -c "from django.contrib.contenttypes.models import ContentType; ContentType.objects.all().delete()"

if [ -f data.json ]; then
  echo "Cargando datos desde data.json..."
  python manage.py loaddata data.json
else
  echo "data.json no encontrado en el directorio actual. Genere el dump con: python manage.py dumpdata --natural-primary --natural-foreign --indent 2 > data.json"
fi

echo "Arrancando servidor de desarrollo..."
python manage.py runserver 0.0.0.0:8000
