from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORIAS = (
        ('electronica', 'Electrónica'),
        ('computacion', 'Computación'),
        ('hogar', 'Hogar'),
        ('ropa', 'Ropa y Accesorios'),
        ('otros', 'Otros'),
    )

    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='otros') # <--- AGREGADO
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    esta_pausado = models.BooleanField(default=False)
    es_vendido = models.BooleanField(default=False)
    imagen_principal = models.ImageField(upload_to='products/')
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=20)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class ProductImage(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='products/gallery/')

class Negotiation(models.Model):
    ESTADOS = (
        ('abierta', 'En negociación'),
        ('vendida', 'Venta concretada'),
        ('cancelada', 'Cancelada'),
    )
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras_intento')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ventas_intento')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierta')
    creada = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    negociacion = models.ForeignKey(Negotiation, on_delete=models.CASCADE, related_name='mensajes')
    emisor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    enviado = models.DateTimeField(auto_now_add=True)