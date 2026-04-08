from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Negotiation

class FramazonTests(TestCase):
    def setUp(self):
        # Configuramos un entorno de prueba
        self.client = Client()
        self.vendedor = User.objects.create_user(username='vendedor', password='pass123', email='vendedor@test.com')
        self.comprador = User.objects.create_user(username='comprador', password='pass123')
        self.producto = Product.objects.create(
            nombre="Producto Test",
            precio=100.00,
            stock=2,
            vendedor=self.vendedor,
            esta_pausado=False
        )

    # 1. Test: La página principal carga correctamente
    def test_index_view(self):
        response = self.client.get(reverse('marketplace:index'))
        self.assertEqual(response.status_code, 200)

    # 2. Test: El buscador filtra productos
    def test_search_functional(self):
        response = self.client.get(reverse('marketplace:index'), {'q': 'Producto Test'})
        self.assertContains(response, "Producto Test")

    # 3. Test: Un usuario no puede contactarse a sí mismo (Lógica del Punto 2)
    def test_self_contact_prevention(self):
        self.client.login(username='vendedor', password='pass123')
        response = self.client.get(reverse('marketplace:iniciar_contacto', args=[self.producto.id]))
        # Debe redirigir al index como configuramos en views.py
        self.assertEqual(response.status_code, 302)

    # 4. Test: El stock disminuye al finalizar una negociación
    def test_stock_reduction_on_sale(self):
        neg = Negotiation.objects.create(producto=self.producto, vendedor=self.vendedor, comprador=self.comprador)
        self.client.login(username='vendedor', password='pass123')
        self.client.get(reverse('marketplace:finalizar_negociacion', args=[neg.id, 'vendido']))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 1)

    # 5. Test: La paginación funciona (Punto 5)
    def test_pagination_exists(self):
        response = self.client.get(reverse('marketplace:index'))
        # Verificamos que el objeto 'productos' en el contexto sea paginado
        self.assertTrue('productos' in response.context)
        self.assertEqual(response.context['productos'].number, 1)

    # 6. Test: El puntito de notificación funciona (Context Processor)
    def test_unread_messages_count(self):
        Negotiation.objects.create(producto=self.producto, vendedor=self.vendedor, comprador=self.comprador, estado='en_progreso')
        self.client.login(username='vendedor', password='pass123')
        response = self.client.get(reverse('marketplace:index'))
        # Verificamos que el conteo de notificaciones sea mayor a 0
        self.assertGreater(response.context['notificaciones_chat'], 0)