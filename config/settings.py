# ============ IMPORTACIONES ============
import os
from pathlib import Path

# ============ DIRECTORIO BASE ============
# Define donde está la carpeta del proyecto (la que contiene manage.py)
# Se usa como referencia para otras rutas
BASE_DIR = Path(__file__).resolve().parent.parent

# ============ SEGURIDAD ============
# ⚠️ IMPORTANTE: Cambiar esto en producción
SECRET_KEY = 'django-insecure-test-key-do-not-use-in-production'

# Modo debug: True = muestra errores detallados (NO usar en producción)
DEBUG = True

# Lista de dominios que pueden acceder a Django
# '*' = permite cualquier dominio (NO usar en producción, poder estar en http, https, localhost, etc.)
ALLOWED_HOSTS = ['*']

# ============ APLICACIONES INSTALADAS ============
# Lista de apps que Django va a usar
INSTALLED_APPS = [
    # Apps por defecto de Django
    'django.contrib.staticfiles',  # Maneja archivos estáticos (CSS, JS, imágenes)
    'django.contrib.admin',        # Panel de administración de Django
    'django.contrib.contenttypes', # Sistema de tipos de contenido
    'django.contrib.auth',         # Sistema de autenticación y usuarios
    'django.contrib.sessions',     # Sistema de sesiones
    'django.contrib.messages',     # Sistema de mensajes
    
    # Apps externas
    'rest_framework',              # Framework para crear APIs REST
    'corsheaders',                 # ⭐ Permite peticiones desde otros dominios (Frontend)
    
    # Tus apps personalizadas
    'core',        # App para funcionalidades principales
    'marketdata',  # App para datos de mercado
    'planning',    # App para planificación
    'tasks',       # App para tareas
]

# ============ MIDDLEWARE ============
# Funciones que procesan todas las peticiones/respuestas
# El ORDEN importa
MIDDLEWARE = [
    # Seguridad
    'django.middleware.security.SecurityMiddleware',
    
    # ⭐ CORS - Debe estar ANTES de SessionMiddleware
    # Permite que el frontend en localhost:3000 hable con este backend
    'corsheaders.middleware.CorsMiddleware',
    
    # Sesiones de usuario
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # Procesa peticiones
    'django.middleware.common.CommonMiddleware',
    
    # Protección CSRF (Cross-Site Request Forgery)
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # Autenticación de usuarios
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # Sistema de mensajes
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ============ CONFIGURATION DE URLs ============
# Indica dónde están las URLs configuradas
ROOT_URLCONF = 'config.urls'

# ============ TEMPLATES ============
# Configuración de cómo Django procesa archivos HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Carpetas con templates (vacío = busca en cada app)
        'APP_DIRS': True,  # Busca templates dentro de cada app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============ BASE DE DATOS ============
# Configuración de la BD donde se guardan los datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Usa SQLite (archivo simple)
        'NAME': BASE_DIR / 'db.sqlite3',         # Archivo de la BD
    }
}

# ============ VALIDACIÓN DE CONTRASEÑAS ============
# Reglas que deben cumplir las contraseñas de los usuarios
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============ INTERNACIONALIZACIÓN ============
# Idioma y zona horaria
LANGUAGE_CODE = 'es-es'  # Español de España
TIME_ZONE = 'America/Mexico_City'  # Zona horaria de México
USE_I18N = True  # Habilita internacionalización
USE_TZ = True   # Usa zonas horarias

# ============ ARCHIVOS ESTÁTICOS ============
# CSS, JS e imágenes que no cambian
STATIC_URL = '/static/'  # URL para acceder a archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Carpeta donde guardos los estáticos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============ CONFIGURACIÓN DE REST FRAMEWORK ============
# Opciones para las APIs REST
REST_FRAMEWORK = {
    # Divide los resultados en páginas (máximo 10 items por página)
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# ============ CONFIGURACIÓN CORS ============
# ⭐ ESTO ES IMPORTANTE PARA QUE EL FRONTEND SE CONECTE
# Especifica qué dominios pueden acceder a esta API
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # Frontend Vue en desarrollo (local)
    'http://127.0.0.1:3000',      # Mismo, pero con IP
    'http://localhost:5173',      # Puerto alternativo de Vite
    'http://127.0.0.1:5173',      # Mismo, pero con IP
]

# Permite enviar cookies entre dominios (necesario para autenticación)
CORS_ALLOW_CREDENTIALS = True
