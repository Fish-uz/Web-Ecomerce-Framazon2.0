# ==============================================================================
# 1. IMPORTACIONES DE MÓDULOS
# ==============================================================================
from django.contrib import admin             # Importa el panel de administración de Django.
from django.urls import path, include        # path para definir rutas, include para conectar otras URLs.
from django.conf import settings             # Permite acceder a las variables definidas en settings.py.
from django.conf.urls.static import static   # Función para servir archivos estáticos/media en desarrollo.

# ==============================================================================
# 2. DEFINICIÓN DE RUTAS (URLPATTERNS)
# ==============================================================================
urlpatterns = [
    # Ruta para el panel de administración (/admin/).
    path('admin/', admin.site.urls),

    # Incluye las rutas de autenticación por defecto de Django (login, logout, password_reset).
    # Estas buscan templates en la carpeta 'registration/'.
    path('accounts/', include('django.contrib.auth.urls')),

    # Conecta las URLs de tu aplicación 'marketplace'. 
    # Al dejarlo vacío (''), se convierte en la página de inicio del sitio.
    path('', include('marketplace.urls')),
]

# ==============================================================================
# 3. CONFIGURACIÓN DE ARCHIVOS MULTIMEDIA (MEDIA)
# ==============================================================================
# Esta validación es crucial: solo sirve archivos de la carpeta 'media' si 
# DEBUG está en True (modo desarrollo).
if settings.DEBUG:
    # Suma a la lista de rutas la ubicación física de las imágenes subidas por los usuarios.
    # settings.MEDIA_URL es el prefijo de la URL (ej. /media/)
    # settings.MEDIA_ROOT es la carpeta real en tu computadora donde están las fotos.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)