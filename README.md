# API de Tareas - Django

Una API simple de Django REST Framework para gestionar tareas.

## Ejecutar con Docker Compose (MySQL)

1. Copia el archivo de ejemplo de variables:
```bash
cp .env.example .env
```

2. Construye y levanta los contenedores:
```bash
docker compose up --build
```

3. La API quedará disponible en:
- `http://localhost:8000/api/`
- `http://localhost:8000/admin/`

## Instalación

##usuario : admin , contra : admin123 
1. **Crear y activar entorno virtual:**
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual (macOS/Linux)
source .venv/bin/activate

# O en Windows:
.venv\Scripts\activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Realizar migraciones:**
```bash
python manage.py migrate
```

3. **Crear superusuario (opcional):**
```bash
python manage.py createsuperuser
```

4. **Ejecutar servidor:**
```bash
python manage.py runserver
```

## Cómo lanzar el programa

### Opción 1: Ejecución rápida (después de la instalación inicial)
```bash
python manage.py runserver
```
La aplicación estará disponible en: `http://localhost:8000/`

### Opción 2: Con puerto específico
```bash
python manage.py runserver 8000
```

### Opción 3: En producción (ejemplo)
```bash
python manage.py runserver 0.0.0.0:8000
```

### Acceder a la aplicación
- **API REST:** `http://localhost:8000/api/`
- **Admin Django:** `http://localhost:8000/admin/`

## Endpoints disponibles

### Tareas
- `GET /api/tasks/` - Listar todas las tareas
- `POST /api/tasks/` - Crear una nueva tarea
- `GET /api/tasks/{id}/` - Obtener una tarea específica
- `PUT /api/tasks/{id}/` - Actualizar una tarea
- `PATCH /api/tasks/{id}/` - Actualización parcial
- `DELETE /api/tasks/{id}/` - Eliminar una tarea

### Endpoints personalizados
- `GET /api/tasks/completed/` - Obtener tareas completadas
- `GET /api/tasks/pending/` - Obtener tareas pendientes

## Ejemplo de uso

### Crear una tarea
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi primera tarea",
    "description": "Una descripción opcional",
    "completed": false
  }'
```

### Listar tareas
```bash
curl http://localhost:8000/api/tasks/
```

### Marcar como completada
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```
