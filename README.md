# RumboPerfecto Backend (Django + DRF)

Backend real para auth + CRUD de viajes/actividades.

## Stack

- Django 4.2
- Django REST Framework
- JWT con `djangorestframework-simplejwt`
- SQLite por defecto (local) o MySQL (Docker)

## Configuracion local

1. Crear entorno virtual e instalar dependencias:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Copiar variables de entorno:

```bash
copy .env.example .env
```

3. Migrar y levantar:

```bash
python manage.py migrate
python manage.py runserver
```

API en `http://localhost:8000/api/`.

## Docker (MySQL)

```bash
docker compose up --build
```

## Endpoints principales

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`

### Viajes

- `GET /api/trips/`
- `POST /api/trips/`
- `GET /api/trips/{id}/`
- `PUT /api/trips/{id}/`
- `PATCH /api/trips/{id}/`
- `DELETE /api/trips/{id}/`

### Actividades

- `GET /api/activities/`
- `POST /api/activities/`
- `GET /api/activities/{id}/`
- `PUT /api/activities/{id}/`
- `PATCH /api/activities/{id}/`
- `DELETE /api/activities/{id}/`
- `GET /api/activities/by_trip/?trip={trip_id}`

### Compatibilidad legacy

- `GET/POST/PUT/PATCH/DELETE /api/tasks/` (sin auth obligatoria)

## Tests

```bash
python manage.py test
```

Cubre flujo de auth y CRUD basico de viajes/actividades con validaciones de rango de dia.
