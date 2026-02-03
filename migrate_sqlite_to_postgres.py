#!/usr/bin/env python
import sys
import sqlite3
import psycopg2
import logging
from pathlib import Path
from datetime import datetime
from django.conf import settings
from decouple import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

SQLITE_DB = BASE_DIR / 'db.sqlite3'
POSTGRES_CONFIG = {
    'database': config('DB_NAME', default='restaurant_db'),
    'user': config('DB_USER', default='postgres'),
    'password': config('DB_PASSWORD', default=''),
    'host': config('DB_HOST', default='localhost'),
    'port': config('DB_PORT', default=5432, cast=int),
}

TABLES_TO_MIGRATE = [
    'availability_restaurant',
    'availability_availabilityrule',
    'availability_season',
    'availability_exceptiondate',
    'reservations_reservation',
    'auth_user',
    'auth_group',
    'auth_permission',
    'django_content_type',
]

def test_postgresql_connection():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.close()
        logger.info("✓ Conexión a PostgreSQL exitosa")
        return True
    except psycopg2.Error as e:
        logger.error(f"✗ Error conectando a PostgreSQL: {e}")
        return False

def test_sqlite_connection():
    try:
        if not SQLITE_DB.exists():
            logger.error(f"✗ Archivo SQLite no encontrado: {SQLITE_DB}")
            return False
        conn = sqlite3.connect(str(SQLITE_DB))
        conn.close()
        logger.info("✓ Conexión a SQLite exitosa")
        return True
    except sqlite3.Error as e:
        logger.error(f"✗ Error conectando a SQLite: {e}")
        return False

def get_sqlite_tables():
    conn = sqlite3.connect(str(SQLITE_DB))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_schema(sqlite_conn, table_name):
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return columns

def migrate_table_data(table_name, sqlite_conn, pg_conn):
    try:
        sqlite_cursor = sqlite_conn.cursor()
        pg_cursor = pg_conn.cursor()
        
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        schema = get_table_schema(sqlite_conn, table_name)
        column_names = [col[1] for col in schema]
        
        if not rows:
            logger.info(f"  - {table_name}: 0 registros")
            return 0
        
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
        
        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            pg_cursor.executemany(insert_query, batch)
        
        pg_conn.commit()
        logger.info(f"  - {table_name}: {len(rows)} registros migrados")
        return len(rows)
        
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"  ✗ Error migrando {table_name}: {e}")
        return 0

def migrate_sequences(pg_conn):
    try:
        cursor = pg_conn.cursor()
        
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """)
        sequences = cursor.fetchall()
        
        for seq in sequences:
            seq_name = seq[0]
            table_name = seq_name.replace('_seq', '')
            
            if '_id_seq' in seq_name:
                base_table = table_name.replace('_id', '')
                cursor.execute(f"SELECT MAX(id) FROM {base_table}")
                max_id = cursor.fetchone()[0]
                
                if max_id:
                    cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH {max_id + 1}")
        
        pg_conn.commit()
        logger.info("✓ Secuencias actualizadas")
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"✗ Error actualizando secuencias: {e}")

def verify_migration(sqlite_conn, pg_conn):
    logger.info("\n📊 Verificación de integridad:")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    all_tables = get_sqlite_tables()
    total_source = 0
    total_dest = 0
    
    for table in all_tables:
        if table.startswith('sqlite_'):
            continue
            
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        source_count = sqlite_cursor.fetchone()[0]
        
        try:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            dest_count = pg_cursor.fetchone()[0]
        except:
            dest_count = 0
        
        total_source += source_count
        total_dest += dest_count
        
        match = "✓" if source_count == dest_count else "✗"
        logger.info(f"  {match} {table}: SQLite={source_count}, PostgreSQL={dest_count}")
    
    return total_source, total_dest

def main():
    logger.info("=" * 70)
    logger.info("MIGRACIÓN SQLite → PostgreSQL")
    logger.info("=" * 70)
    
    if not test_sqlite_connection():
        sys.exit(1)
    
    if not test_postgresql_connection():
        sys.exit(1)
    
    logger.info("\n🔄 Iniciando migración de datos...\n")
    
    sqlite_conn = sqlite3.connect(str(SQLITE_DB))
    pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
    
    tables = get_sqlite_tables()
    total_migrated = 0
    
    logger.info("Migrando datos:")
    for table in tables:
        if table.startswith('sqlite_'):
            continue
        migrated = migrate_table_data(table, sqlite_conn, pg_conn)
        total_migrated += migrated
    
    migrate_sequences(pg_conn)
    
    logger.info("\n" + "=" * 70)
    total_source, total_dest = verify_migration(sqlite_conn, pg_conn)
    logger.info("=" * 70)
    
    if total_source == total_dest:
        logger.info(f"\n✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        logger.info(f"  Total de registros: {total_dest}")
    else:
        logger.warning(f"\n⚠ ADVERTENCIA: Discrepancia en conteos")
        logger.warning(f"  Origen: {total_source}, Destino: {total_dest}")
    
    logger.info("\n📝 Próximos pasos:")
    logger.info("  1. Verificar datos en PostgreSQL")
    logger.info("  2. Cambiar DATABASES en settings.py a PostgreSQL")
    logger.info("  3. Ejecutar: python manage.py migrate")
    logger.info("  4. Hacer backup de db.sqlite3")
    
    sqlite_conn.close()
    pg_conn.close()
    
    logger.info("\n✓ Proceso finalizado\n")

if __name__ == '__main__':
    main()
