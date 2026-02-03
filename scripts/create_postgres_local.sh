#!/usr/bin/env bash
set -euo pipefail

DB_NAME=${DB_NAME:-restaurant_availability}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}

echo "Creando rol y base de datos PostgreSQL (si no existen)..."

sudo -u postgres psql <<SQL
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
   END IF;
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
      CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
   END IF;
END
$do$;
SQL

echo "Configuración completada."

echo "Conectar: psql -U ${DB_USER} -d ${DB_NAME} -h localhost -W"
