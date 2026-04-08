import os
from decouple import config
from pathlib import Path

# ==============================================================================
# 1. CONFIGURACIÓN DE RUTAS (PATHS)
# ==============================================================================
# Define la ruta raíz del proyecto. Facilita el uso de rutas relativas.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# 2. AJUSTES DE SEGURIDAD Y DESARROLLO
# ==============================================================================
# Clave secreta para firmar cookies y sesiones. ¡Mantener privada en producción!

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Dominios/IPs desde los cuales se puede acceder al sitio (vacío = localhost).
ALLOWED_HOSTS = []


# ==============================================================================
# 3. DEFINICIÓN DE APLICACIONES (APPS)
# ==============================================================================
INSTALLED_APPS = [
    # Apps integradas de Django
    'django.contrib.admin',         # Panel de administración.
    'django.contrib.auth',          # Sistema de autenticación.
    'django.contrib.contenttypes',  # Permite relaciones entre modelos.
    'django.contrib.sessions',      # Gestión de sesiones de usuario.
    'django.contrib.messages',      # Sistema de notificaciones flash.
    'django.contrib.staticfiles',   # Gestión de archivos CSS, JS e imágenes.
    'django_extensions',
    
    # App del Proyecto
    'marketplace',                  # Tu aplicación principal de ventas.
]


# ==============================================================================
# 4. CAPAS DE INTERCEPCIÓN (MIDDLEWARE)
# ==============================================================================
# Funciones que procesan la petición antes de llegar a la vista y antes de la respuesta.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',             # Protección contra ataques CSRF.
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Asocia usuarios con peticiones.
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ==============================================================================
# 5. RUTAS Y TEMPLATES
# ==============================================================================
# Indica dónde está el archivo de rutas principal.
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Carpetas globales de templates (opcional).
        'APP_DIRS': True, # Busca la carpeta 'templates' dentro de cada app instalada.
        'OPTIONS': {
            'context_processors': [
                # Procesadores por defecto
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Procesadores personalizados para el chat
                'marketplace.views.mensajes_pendientes', # Inyecta notificaciones en todos los templates.
            ],
        },
    },
]

# Configuración del servidor de aplicaciones (interfaz de servidor web).
WSGI_APPLICATION = 'core.wsgi.application'


# ==============================================================================
# 6. BASE DE DATOS
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Motor de base de datos (ligero para desarrollo).
        'NAME': BASE_DIR / 'db.sqlite3',        # Archivo donde se guarda la data.
    }
}


# ==============================================================================
# 7. VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================
# Reglas para asegurar que las contraseñas de los usuarios sean seguras.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================================================================
# 8. INTERNACIONALIZACIÓN Y HORARIOS
# ==============================================================================
LANGUAGE_CODE = 'en-us' # Idioma del panel de admin.
TIME_ZONE = 'UTC'       # Zona horaria global.
USE_I18N = True         # Activa el sistema de traducción.
USE_TZ = True           # Usa fechas con zona horaria consciente.


# ==============================================================================
# 9. ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# ==============================================================================
# Archivos Estáticos (CSS, JS, Logos del sistema)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Carpeta de desarrollo.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Carpeta donde se recolectan para producción.

# Archivos Multimedia (Imágenes de productos subidas por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Carpeta física donde se guardan las fotos.


# ==============================================================================
# 10. FLUJO DE AUTENTICACIÓN
# ==============================================================================
# A dónde enviar al usuario después de entrar o salir del sistema.
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'marketplace:index'


# ==============================================================================
# 11. REGISTRO DE ERRORES (LOGGING)
# ==============================================================================
# Configuración para guardar errores y eventos en un archivo llamado 'debug.log'.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            # Formato: [HORA] NIVEL MODULO MENSAJE
            'format': '{asctime} [{levelname}] {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}