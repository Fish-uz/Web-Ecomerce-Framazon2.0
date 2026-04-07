from django.contrib import admin
from .models import Product, Negotiation, Message

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'vendedor')
    search_fields = ('nombre',)

@admin.register(Negotiation)
class NegotiationAdmin(admin.ModelAdmin):
    list_display = ('producto', 'comprador', 'vendedor', 'estado', 'creada')
    list_filter = ('estado',)

admin.site.register(Message)