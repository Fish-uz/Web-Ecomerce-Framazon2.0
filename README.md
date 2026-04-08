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

Stack Tecnológico
Backend: Django 5.x (Python)
Frontend: HTML5, CSS3 (Custom Styles), Bootstrap 5, JavaScript (Vanilla)
Base de Datos: SQLite (Desarrollo) / PostgreSQL (Producción)
Iconos: Bootstrap Icons

# Instalación y Configuración
Clonar el repositorio:
Bash
git clone https://github.com/tu-usuario/framazon.git
cd framazon

Configurar el entorno virtual:
Bash
python -m venv venv
source venv/Scripts/activate  # En Windows

Instalar dependencias:
Bash
pip install -r requirements.txt

Aplicar migraciones y correr servidor:
Bash
python manage.py migrate
python manage.py runserver
🧪 Pruebas Automatizadas

# Este proyecto incluye una suite de pruebas unitarias para garantizar la estabilidad:
Bash
python manage.py test marketplace
Se evalúan flujos críticos: creación de productos, seguridad de login y lógica de stock.