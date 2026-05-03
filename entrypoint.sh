#!/bin/sh
set -e

echo "▶ Esperando a que MySQL esté listo..."
until python manage.py showmigrations > /dev/null 2>&1; do
    echo "  MySQL no disponible todavía, reintentando en 3 s..."
    sleep 3
done

echo "▶ Aplicando migraciones..."
python manage.py migrate --noinput

echo "▶ Sembrando catálogo de servicios..."
python manage.py seed_services

echo "▶ Colectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "▶ Iniciando Gunicorn en 0.0.0.0:8000..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --reload \
    --access-logfile - \
    --error-logfile -
