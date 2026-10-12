# Framazon

Framazon es un marketplace desarrollado con Django para publicar, explorar y
negociar productos entre usuarios.

## Funcionalidades

- Registro, inicio y cierre de sesión.
- Catálogo de productos con búsqueda, categorías y paginación.
- Publicación, edición y pausa de productos.
- Imagen principal y galería de hasta cinco imágenes adicionales por producto.
- Gestión de inventario al completar una venta.
- Negociaciones privadas con chat entre comprador y vendedor.
- Panel de perfil con publicaciones, compras y ventas.
- Administración de Django para gestionar productos, imágenes y negociaciones.

## Tecnologías

- Python 3.12 o superior
- Django 6
- SQLite para desarrollo local
- Bootstrap 5 y Bootstrap Icons
- Pillow para el manejo de imágenes

## Instalación

### 1. Obtener el proyecto

```bash
git clone https://github.com/Fish-uz/Web-Ecomerce-Framazon2.0.git
cd Web-Ecomerce-Framazon2.0
```

### 2. Crear el entorno virtual

En Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En macOS o Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Si PowerShell bloquea la activación, ejecuta esto una vez en la ventana actual
y vuelve a activar el entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto, junto a `manage.py`:

```env
SECRET_KEY=una-clave-secreta-larga-y-unica
DEBUG=True
```

Para generar una clave segura:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Ejecutar el proyecto

Aplica las migraciones y arranca el servidor:

```bash
python manage.py migrate
python manage.py runserver
```

Abre <http://127.0.0.1:8000/> en el navegador. Para detener el servidor, usa
`Ctrl + C` en la terminal.

En ejecuciones posteriores, solo activa el entorno virtual y usa:

```bash
python manage.py runserver
```

## Administración

Para crear un usuario administrador:

```bash
python manage.py createsuperuser
```

Después inicia el servidor y visita <http://127.0.0.1:8000/admin/>.

## Pruebas

```bash
python manage.py test marketplace
```

## Estructura del proyecto

```text
core/          Configuración general y rutas globales
marketplace/   Modelos, vistas, formularios, plantillas y pruebas
static/        Archivos CSS, JavaScript e imágenes estáticas
media/         Imágenes cargadas para productos en desarrollo local
```

## Despliegue

Antes de publicar la aplicación, configura `DEBUG=False`, una nueva
`SECRET_KEY`, `ALLOWED_HOSTS`, almacenamiento persistente para archivos
multimedia, HTTPS y ejecuta:

```bash
python manage.py collectstatic
```
