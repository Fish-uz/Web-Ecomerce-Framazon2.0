from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Message, Product, Negotiation

class FramazonTests(TestCase):
    def setUp(self):
        # Configuramos un entorno de prueba
        self.client = Client()
        self.vendedor = User.objects.create_user(username='vendedor', password='pass123', email='vendedor@test.com')
        self.comprador = User.objects.create_user(username='comprador', password='pass123')
        self.intruso = User.objects.create_user(username='intruso', password='pass123')
        self.producto = Product.objects.create(
            nombre="Producto Test",
            descripcion="Producto de prueba para validar el marketplace.",
            precio=100.00,
            stock=2,
            vendedor=self.vendedor,
            esta_pausado=False,
            imagen_principal=SimpleUploadedFile(
                'producto.gif',
                b'GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
                content_type='image/gif',
            ),
            email_contacto='vendedor@test.com',
            telefono_contacto='04121234567',
        )

    # 1. Test: La página principal carga correctamente
    def test_index_view(self):
        response = self.client.get(reverse('marketplace:index'))
        self.assertEqual(response.status_code, 200)

    def test_login_authenticates_and_redirects_to_the_catalog(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'comprador', 'password': 'pass123'},
        )
        self.assertRedirects(response, reverse('marketplace:index'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.comprador.id)

    # 2. Test: El buscador filtra productos
    def test_search_functional(self):
        response = self.client.get(reverse('marketplace:index'), {'q': 'Producto Test'})
        self.assertContains(response, "Producto Test")

    # 3. Test: Un usuario no puede contactarse a sí mismo (Lógica del Punto 2)
    def test_self_contact_prevention(self):
        self.client.login(username='vendedor', password='pass123')
        response = self.client.post(reverse('marketplace:iniciar_contacto', args=[self.producto.id]), {'msg': 'Hola'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Negotiation.objects.count(), 0)

    # 4. Test: El stock disminuye al finalizar una negociación
    def test_stock_reduction_on_sale(self):
        neg = Negotiation.objects.create(producto=self.producto, vendedor=self.vendedor, comprador=self.comprador)
        self.client.login(username='vendedor', password='pass123')
        self.client.post(reverse('marketplace:finalizar_negociacion', args=[neg.id, 'vendido']))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 1)
        neg.refresh_from_db()
        self.assertEqual(neg.estado, 'vendida')

        self.client.post(reverse('marketplace:finalizar_negociacion', args=[neg.id, 'vendido']))
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
        Negotiation.objects.create(producto=self.producto, vendedor=self.vendedor, comprador=self.comprador, estado='abierta')
        self.client.login(username='vendedor', password='pass123')
        response = self.client.get(reverse('marketplace:index'))
        # Verificamos que el conteo de notificaciones sea mayor a 0
        self.assertGreater(response.context['notificaciones_chat'], 0)

    def test_chat_rejects_a_user_outside_the_negotiation(self):
        neg = Negotiation.objects.create(producto=self.producto, vendedor=self.vendedor, comprador=self.comprador)
        self.client.login(username='intruso', password='pass123')
        response = self.client.post(reverse('marketplace:chat', args=[neg.id]), {'msg': 'Mensaje no autorizado'})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Message.objects.exists())

    def test_state_changing_views_reject_get_requests(self):
        neg = Negotiation.objects.create(producto=self.producto, vendedor=self.vendedor, comprador=self.comprador)
        self.client.login(username='vendedor', password='pass123')
        response = self.client.get(reverse('marketplace:pausar_producto', args=[self.producto.id]))
        self.assertEqual(response.status_code, 405)
        response = self.client.get(reverse('marketplace:finalizar_negociacion', args=[neg.id, 'vendido']))
        self.assertEqual(response.status_code, 405)

    def test_buyer_can_start_only_one_negotiation_per_product(self):
        self.client.login(username='comprador', password='pass123')
        url = reverse('marketplace:iniciar_contacto', args=[self.producto.id])
        self.client.post(url, {'msg': '¿Sigue disponible?'})
        self.client.post(url, {'msg': 'Me interesa el producto.'})
        self.assertEqual(Negotiation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)
