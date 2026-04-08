# ==============================================================================
# 1. IMPORTACIONES Y CONFIGURACIÓN INICIAL
# ==============================================================================
from django.urls import path  # Función para definir cada ruta individual.
from . import views           # Importamos todas las funciones de views.py de esta app.

# Define el espacio de nombres para usar etiquetas como {% url 'marketplace:index' %}
app_name = 'marketplace'

# ==============================================================================
# 2. DEFINICIÓN DE RUTAS (URLPATTERNS)
# ==============================================================================
urlpatterns = [
    
    # --- NAVEGACIÓN Y VISTA PÚBLICA ---
    # Página principal que muestra el catálogo de productos.
    path('', views.index, name='index'),
    
    # Detalle individual de un producto (usa el ID para saber cuál mostrar).
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),

    # --- GESTIÓN DE PRODUCTOS (VENDEDOR) ---
    # Formulario para subir un nuevo producto al marketplace.
    path('vender/', views.crear_producto, name='crear_producto'), 
    
    # Permite al vendedor modificar los datos de un producto ya existente.
    path('producto/<int:product_id>/editar/', views.editar_producto, name='editar_producto'),
    
    # Opción para ocultar/mostrar un producto sin borrarlo de la base de datos.
    path('producto/<int:product_id>/pausar/', views.pausar_producto, name='pausar_producto'),

    # --- SISTEMA DE NEGOCIACIÓN Y CHAT ---
    # Punto de entrada cuando un comprador hace clic en "Contactar".
    path('contactar/<int:product_id>/', views.iniciar_contacto, name='iniciar_contacto'),
    
    # El panel central donde ves tus compras actuales y ventas pendientes.
    path('mis-negociaciones/', views.mis_negociaciones, name='mis_negociaciones'),
    
    # Procesa el envío y recepción de mensajes dentro de una negociación.
    path('chat/<int:negociacion_id>/', views.chat, name='chat'),
    
    # Rutas para cerrar un trato (Vendido o Cancelado). 
    # Se incluyen dos versiones para evitar errores de navegación.
    path('negociacion/<int:neg_id>/finalizar/<str:accion>/', views.finalizar_negociacion, name='finalizar_negociacion'),
    path('finalizar-negociacion/<int:neg_id>/<str:accion>/', views.finalizar_negociacion, name='finalizar_negociacion'),

    # --- CUENTA Y PERFIL ---
    # Registro de nuevos usuarios en la plataforma.
    path('registro/', views.registro, name='registro'),
    
    # Espacio personal del usuario (datos, foto de perfil, etc.).
    path('perfil/', views.perfil, name='perfil'),
]