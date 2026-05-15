# RumboPerfecto — Backend (Django + DRF)

API REST para autenticación (JWT), catálogo de servicios (`marketdata`), planes de viaje y reservas (`planning`).

## Stack

- Python 3.10+
- Django 4.2
- Django REST Framework
- JWT: `djangorestframework-simplejwt` (refresh en lista negra)
- **MySQL** en desarrollo y producción típica (ver `.env.example`)
- SQLite **solo** en tests (`config.settings_test`)

## Estructura del repositorio

En el monorepo, el código Django vive en **`RumboPerfecto/RumboPerfecto/`** (junto a `manage.py`). El frontend Vue está en **`rumboperfecto-vue/`**.

## Configuración local

### 1. Entorno virtual y dependencias

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. MySQL y variables de entorno

Crea la base y usuario que coincidan con tu `.env`. Copia la plantilla:

**Windows:** `copy .env.example .env`  
**macOS / Linux:** `cp .env.example .env`

Ajusta al menos `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` si MySQL no está en `127.0.0.1:3306`. `CORS_ALLOWED_ORIGINS` debe incluir el origen del frontend (por defecto Vue en `http://localhost:3000`).

### 3. Migraciones y servidor

```bash
python manage.py migrate
python manage.py runserver
```

La API queda en **`http://localhost:8000/api/`**. Panel admin: `http://localhost:8000/admin/`.

### 4. Estáticos (opcional)

Si usas `STATIC_ROOT` y el admin en producción:

```bash
python manage.py collectstatic --noinput
```

## Docker (MySQL + web)

Desde esta misma carpeta (donde están `docker-compose.yml` y `Dockerfile`):

```bash
docker compose up --build
```

## Endpoints principales

Rutas definidas en `config/urls.py`.

### Autenticación y perfil (`core`)

| Método | Ruta |
|--------|------|
| POST | `/api/auth/register/` |
| POST | `/api/auth/login/` |
| POST | `/api/auth/refresh/` |
| POST | `/api/auth/logout/` |
| GET / PATCH | `/api/auth/me/` |
| POST | `/api/auth/change-password/` |
| POST | `/api/auth/seller/` |
| GET | `/api/auth/mis-servicios/` |
| PATCH | `/api/auth/mis-servicios/<id_servicio>/` |
| GET | `/api/auth/mis-servicios/<id_servicio>/reservas/` |
| PATCH | `/api/auth/mis-servicios/<id_servicio>/reservas/<pk>/` |

### Reservas cliente (`planning`)

| Método | Ruta |
|--------|------|
| GET / POST | `/api/auth/mis-reservas/` |
| GET / PATCH / DELETE | `/api/auth/mis-reservas/<pk>/` |

### Planes e ítems (`planning`)

| Método | Ruta |
|--------|------|
| GET / POST | `/api/auth/mis-planes/` |
| GET / PATCH / DELETE | `/api/auth/mis-planes/<pk>/` |
| GET / POST | `/api/auth/mis-planes/<pk>/items/` |
| GET / PATCH / DELETE | `/api/auth/mis-planes/<pk>/items/<item_pk>/` |

### Utilidades

| Método | Ruta |
|--------|------|
| GET | `/api/auth/geocode/?q=...` — geocodificación (Nominatim), requiere JWT |
| GET | `/api/tipos-servicio/` |

### Catálogo público (`marketdata`)

| Método | Ruta |
|--------|------|
| GET | `/api/servicios/` |
| GET | `/api/servicios/<id_servicio>/` |
| GET / POST | `/api/servicios/<id_servicio>/resenas/` (POST con JWT) |

**Nota:** Al guardar un servicio en `PATCH /api/auth/mis-servicios/...`, si envías dirección, ciudad y país (y no fuerzas coordenadas manualmente en el payload), el servidor puede **rellenar latitud y longitud** vía geocodificación cuando la consulta tiene sentido.

## Tests

Usan **SQLite en memoria**; no hace falta MySQL para ejecutarlos:

```bash
python manage.py test --settings=config.settings_test
```

Los casos están bajo **`tests/`** (`tests.apps.TestsConfig` solo se incluye en `INSTALLED_APPS` con ese settings).

```
tests/
  apps.py
  core/
    test_auth.py
    test_profile_and_services.py   # perfil, mis servicios, patch + geocode servicio (mocks)
  marketdata/
    test_catalogo_servicios.py
    test_resenas.py
  planning/
    test_reservas.py
    test_planes_y_tipos.py
    test_geocode.py
    test_itemplan_reserva_coords.py
    test_vendedor_reservas.py
  config/
    test_urls.py
```

## Nota sobre apps retiradas

Las apps `travel` y `tasks` ya no forman parte del proyecto. Si en algún momento se aplicaron sus migraciones, podrían quedar tablas huérfanas en la base de desarrollo; en ese caso conviene eliminarlas a mano o recrear la base.
