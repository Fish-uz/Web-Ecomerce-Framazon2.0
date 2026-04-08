# Framazon - Marketplace Moderno con Django
Framazon es una plataforma de comercio electrónico funcional que permite a los usuarios publicar 
productos, gestionar inventarios y entablar negociaciones directas a través de un sistema de chat 
integrado. El proyecto está inspirado en la estética de Amazon, priorizando la simplicidad y la seguridad.

# Características Principales
Gestión de Catálogo
Publicación Multimedia: Subida de imagen principal y galería de hasta 5 fotos adicionales.
Filtros Dinámicos: Búsqueda por texto y filtrado por categorías (Electrónica, Hogar, Computación, etc.).
Control de Stock: Actualización automática del inventario al concretar ventas.

Sistema de Negociación (Chat)
Chat en Tiempo Real: Flujo de mensajería privado entre comprador y vendedor.
Gestión de Tratos: Posibilidad de pausar publicaciones, marcar como vendido o cancelar negociaciones.
Notificaciones Globales: Contador de mensajes pendientes disponible en toda la aplicación.

Seguridad y Perfiles
Autenticación Completa: Registro, login y gestión de sesiones.
Protección de Rutas: Solo los usuarios autenticados pueden vender o negociar.
Validación de Propiedad: Solo el dueño de un producto puede editarlo o pausarlo.

# Tecnologías Utilizadas
* **Backend:** [Django 5.0](https://www.djangoproject.com/) (Python Framework)
* **Base de Datos:** SQLite (Desarrollo)
* **Frontend:** Bootstrap 5.3, Bootstrap Icons y Google Fonts (Inter)
* **Gestión de Imágenes:** Pillow (Procesamiento de archivos multimedia)
* **Seguridad:** Python-Decouple (Manejo de variables de entorno)
* **Herramientas:** Django Context Processors (Notificaciones en tiempo real) y Django Forms (Validación avanzada).

# Instrucciones de Instalación (Paso a paso)

## Instalación y Configuración

Sigue estos pasos para ejecutar **Framazon** localmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Fish-uz/Web-Ecomerce-Framazon2.0.git](https://github.com/Fish-uz/Web-Ecomerce-Framazon2.0.git)
   cd Web-Ecomerce-Framazon2.0

Crear y activar el entorno virtual:
Bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

Instalar dependencias:
Bash
pip install -r requirements.txt
Configurar variables de entorno:

Crea un archivo .env en la raíz.

Agrega tu SECRET_KEY y define DEBUG=True.

Realizar migraciones y arrancar:
Bash
python manage.py migrate
python manage.py runserver
Visita http://127.0.0.1:8000 en tu navegador.

Pruebas Automatizadas
# Este proyecto incluye una suite de pruebas unitarias para garantizar la estabilidad:
Bash
python manage.py test marketplace
Se evalúan flujos críticos: creación de productos, seguridad de login y lógica de stock.
