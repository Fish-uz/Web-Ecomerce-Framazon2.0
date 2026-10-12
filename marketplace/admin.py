# ==============================================================================
# 1. IMPORTACIONES
# ==============================================================================
from django.contrib import admin  # Herramientas base del administrador de Django
from .models import Product, ProductImage, Negotiation, Message

# ==============================================================================
# 2. CONFIGURACIÓN DEL MODELO 'PRODUCT' (PRODUCTOS)
# ==============================================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Define qué columnas se verán en la tabla principal del administrador
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'esta_pausado', 'es_vendido', 'vendedor')
    
    # Crea una barra de búsqueda que filtra específicamente por el nombre del producto
    search_fields = ('nombre', 'vendedor__username')
    list_filter = ('categoria', 'esta_pausado', 'es_vendido')

# ==============================================================================
# 3. CONFIGURACIÓN DEL MODELO 'NEGOTIATION' (CHATS/VENTAS)
# ==============================================================================
@admin.register(Negotiation)
class NegotiationAdmin(admin.ModelAdmin):
    # Columnas visibles para rastrear quién le compra a quién y el estado del trato
    list_display = ('producto', 'comprador', 'vendedor', 'estado', 'creada')
    
    # Agrega un panel lateral de filtros para separar rápido 'Vendidos' de 'Abiertos'
    list_filter = ('estado',)

# ==============================================================================
# 4. REGISTRO DEL MODELO 'MESSAGE' (MENSAJES)
# ==============================================================================
# Registro simple: Usa la configuración por defecto de Django para ver los mensajes
# enviados entre usuarios dentro de cada negociación.
admin.site.register(Message)
admin.site.register(ProductImage)
