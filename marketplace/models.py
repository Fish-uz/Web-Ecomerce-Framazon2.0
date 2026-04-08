# ==============================================================================
# 1. IMPORTACIONES
# ==============================================================================
from django.db import models              # Herramientas para crear tablas en la DB.
from django.contrib.auth.models import User # Modelo de usuario oficial de Django.

# ==============================================================================
# 2. MODELO DE PRODUCTO (LA ENTIDAD CENTRAL)
# ==============================================================================
class Product(models.Model):
    # Opciones predefinidas para el campo categoría
    CATEGORIAS = (
        ('electronica', 'Electrónica'),
        ('computacion', 'Computación'),
        ('hogar', 'Hogar'),
        ('ropa', 'Ropa y Accesorios'),
        ('otros', 'Otros'),
    )

    # Relación: Un usuario puede tener muchos productos (vendedor)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos')
    
    # Datos básicos del producto
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='otros')
    descripcion = models.TextField()
    
    # Precios y cantidades
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    
    # Estados lógicos para control de visibilidad y venta
    esta_pausado = models.BooleanField(default=False) # Permite ocultar el producto sin borrarlo
    es_vendido = models.BooleanField(default=False)  # Marca si el producto ya no está disponible
    
    # Archivos multimedia: Imagen destacada
    imagen_principal = models.ImageField(upload_to='products/')
    
    # Información de contacto directo
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=20)
    
    # Registro de tiempo automático al crear el objeto
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Define cómo se muestra el objeto en el panel de admin (por su nombre)
        return self.nombre

# ==============================================================================
# 3. GALERÍA DE IMÁGENES (RELACIÓN 1 a MUCHOS)
# ==============================================================================
class ProductImage(models.Model):
    # Relaciona varias fotos adicionales a un solo producto
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='products/gallery/')

# ==============================================================================
# 4. NEGOCIACIÓN (EL VÍNCULO COMPRADOR-VENDEDOR)
# ==============================================================================
class Negotiation(models.Model):
    ESTADOS = (
        ('abierta', 'En negociación'),
        ('vendida', 'Venta concretada'),
        ('cancelada', 'Cancelada'),
    )
    
    # Conecta el trato con el producto específico
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Identifica a las dos partes involucradas (usuarios de Django)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras_intento')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ventas_intento')
    
    # Controla en qué punto está la transacción
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierta')
    creada = models.DateTimeField(auto_now_add=True)

# ==============================================================================
# 5. MENSAJES (EL CHAT INTERNO)
# ==============================================================================
class Message(models.Model):
    # Relaciona el mensaje con una negociación específica (el "hilo" del chat)
    negociacion = models.ForeignKey(Negotiation, on_delete=models.CASCADE, related_name='mensajes')
    
    # Quién escribió el mensaje
    emisor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Contenido del texto y marca de tiempo exacta (Fecha y Hora)
    contenido = models.TextField()
    enviado = models.DateTimeField(auto_now_add=True)