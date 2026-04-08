# ==============================================================================
# 1. IMPORTACIÓN DE HERRAMIENTAS
# ==============================================================================
# Importa la clase base AppConfig desde el núcleo de Django. 
# Esta clase contiene toda la lógica necesaria para gestionar el ciclo de vida de una App.
from django.apps import AppConfig


# ==============================================================================
# 2. DEFINICIÓN DE LA CLASE DE CONFIGURACIÓN
# ==============================================================================
# Esta clase define las propiedades específicas de tu aplicación 'marketplace'.
class MarketplaceConfig(AppConfig):
    
    # Define el tipo de campo automático por defecto para las llaves primarias (ID).
    # Aunque no esté explícito en tu código original, Django suele usar BigAutoField por defecto.
    default_auto_field = 'django.db.models.BigAutoField'

    # Define el nombre de la aplicación dentro del proyecto. 
    # Es la ruta completa que Django usará para identificarla en INSTALLED_APPS.
    name = 'marketplace'