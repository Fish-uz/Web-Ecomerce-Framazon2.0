from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.index, name='index'),
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),
    # Mantenemos 'crear_producto' para que tus botones de "Vender" sigan funcionando
    path('vender/', views.crear_producto, name='crear_producto'), 
    path('contactar/<int:product_id>/', views.iniciar_contacto, name='iniciar_contacto'),
    path('chat/<int:negociacion_id>/', views.chat, name='chat'),
    path('mis-negociaciones/', views.mis_negociaciones, name='mis_negociaciones'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('producto/<int:product_id>/editar/', views.editar_producto, name='editar_producto'),
    path('producto/<int:product_id>/pausar/', views.pausar_producto, name='pausar_producto'),
    path('negociacion/<int:neg_id>/finalizar/<str:accion>/', views.finalizar_negociacion, name='finalizar_negociacion'),
    path('finalizar-negociacion/<int:neg_id>/<str:accion>/', views.finalizar_negociacion, name='finalizar_negociacion'),
]