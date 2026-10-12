from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import Product, Negotiation, Message, ProductImage
from .forms import ProductForm

# ==============================================================================
# 1. VISTAS PÚBLICAS (ACCESIBLES POR TODOS)
# ==============================================================================

def index(request):
    """ Muestra el catálogo de productos con búsqueda, filtros y paginación. """
    query = request.GET.get('q')           # Captura el texto de búsqueda.
    cat_filter = request.GET.get('categoria') # Captura el filtro de categoría.
    
    # Solo mostramos productos con stock y que no estén pausados por el vendedor.
    productos_list = Product.objects.filter(
        stock__gt=0,
        esta_pausado=False,
        es_vendido=False,
    ).select_related('vendedor')
    
    if query:
        # Filtra por nombre o descripción usando el operador OR (|).
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    
    if cat_filter:
        productos_list = productos_list.filter(categoria=cat_filter)
    
    # Paginación: Muestra 12 productos por página.
    paginator = Paginator(productos_list, 12)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)
        
    return render(request, 'marketplace/index.html', {
        'productos': productos, 
        'query': query,
        'cat_actual': cat_filter
    })

def product_detail(request, product_id):
    """ Muestra la información completa de un producto y su chat de negociación. """
    producto = get_object_or_404(Product, id=product_id)
    imagenes_extra = producto.imagenes.all() 
    
    negociacion = None
    mensajes = None
    if request.user.is_authenticated:
        # Identificamos quién está viendo la página para cargar el chat correcto.
        comprador_id = request.GET.get('comprador')
        
        if producto.vendedor == request.user:
            # LÓGICA VENDEDOR: Si viene de 'Atender', carga el chat con ese comprador específico.
            if comprador_id:
                negociacion = Negotiation.objects.filter(
                    producto=producto,
                    comprador_id=comprador_id,
                ).first()
            else:
                # Si no, carga la conversación más reciente de este producto.
                negociacion = Negotiation.objects.filter(producto=producto).first()
        else:
            # LÓGICA COMPRADOR: Carga su propia conversación con el dueño del producto.
            negociacion = Negotiation.objects.filter(
                producto=producto,
                comprador=request.user,
            ).first()

        if negociacion:
            mensajes = negociacion.mensajes.select_related('emisor').all()

    return render(request, 'marketplace/product_detail.html', {
        'producto': producto,
        'imagenes_extra': imagenes_extra,
        'negociacion': negociacion,
        'mensajes': mensajes,
    })

def registro(request):
    """ Gestiona la creación de nuevas cuentas de usuario. """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Inicia sesión automáticamente tras el registro.
            return redirect('marketplace:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})

# ==============================================================================
# 2. GESTIÓN DE PERFIL Y PRODUCTOS (REQUIERE LOGIN)
# ==============================================================================

@login_required
def perfil(request):
    """ Panel de control del usuario: sus productos y su historial de compras. """
    mis_productos = Product.objects.filter(vendedor=request.user)
    compras_finalizadas = Negotiation.objects.filter(
        comprador=request.user,
        estado='vendida',
    ).select_related('producto', 'vendedor')
    ventas_exitosas = Negotiation.objects.filter(
        vendedor=request.user,
        estado='vendida',
    ).select_related('producto', 'comprador')
    
    return render(request, 'marketplace/perfil.html', {
        'mis_productos': mis_productos,
        'compras_finalizadas': compras_finalizadas,
        'count_compras': compras_finalizadas.count(),
        'ventas_exitosas': ventas_exitosas,
    })

@login_required
def crear_producto(request):
    """ Permite subir un producto y procesar hasta 5 imágenes adicionales. """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_prod = form.save(commit=False)
            nuevo_prod.vendedor = request.user
            nuevo_prod.save() # Guarda el producto.

            # Procesa la lista de archivos para la galería.
            images = request.FILES.getlist('extra_imgs')
            for img in images[:5]:
                ProductImage.objects.create(producto=nuevo_prod, imagen=img)
                
            return redirect('/perfil/#publicaciones')
    else:
        form = ProductForm(initial={'email_contacto': request.user.email})
    return render(request, 'marketplace/vender.html', {'form': form})

@login_required
def editar_producto(request, product_id):
    """ Permite al dueño modificar su producto e imágenes. """
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            images = request.FILES.getlist('extra_imgs')
            if images:
                producto.imagenes.all().delete() # Reemplaza imágenes viejas por nuevas.
                for img in images[:5]:
                    ProductImage.objects.create(producto=producto, imagen=img)
            return redirect('/perfil/#publicaciones')
    else:
        form = ProductForm(instance=producto)
    return render(request, 'marketplace/vender.html', {'form': form, 'editando': True})

@login_required
@require_POST
def pausar_producto(request, product_id):
    """ Alterna la visibilidad del producto en el catálogo. """
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    producto.esta_pausado = not producto.esta_pausado
    producto.save()
    return redirect('/perfil/#publicaciones')

# ==============================================================================
# 3. FLUJO DE NEGOCIACIÓN Y CHAT
# ==============================================================================

@login_required
@require_POST
def iniciar_contacto(request, product_id):
    """ Crea el vínculo inicial entre comprador y vendedor. """
    producto = get_object_or_404(Product, id=product_id)
    
    if producto.vendedor == request.user:
        return redirect('marketplace:product_detail', product_id=producto.id)

    if producto.esta_pausado or producto.es_vendido or producto.stock < 1:
        messages.error(request, 'Este producto ya no está disponible para negociar.')
        return redirect('marketplace:product_detail', product_id=producto.id)

    msg_contenido = request.POST.get('msg', '').strip()
    if not msg_contenido:
        messages.error(request, 'Escribe un mensaje para iniciar la negociación.')
        return redirect(f"{reverse('marketplace:product_detail', args=[producto.id])}?chat=abierto")

    negociacion, created = Negotiation.objects.get_or_create(
        producto=producto,
        comprador=request.user,
        defaults={'vendedor': producto.vendedor},
    )

    if negociacion.estado != 'abierta':
        messages.error(request, 'Esta negociación ya fue cerrada.')
    else:
        Message.objects.create(negociacion=negociacion, emisor=request.user, contenido=msg_contenido)
    
    return redirect(f'/producto/{producto.id}/?chat=abierto')

@login_required
def mis_negociaciones(request):
    """ Lista todas las conversaciones donde el usuario compra o vende. """
    compras = Negotiation.objects.filter(comprador=request.user).select_related('producto', 'vendedor')
    # select_related optimiza la consulta para obtener datos del producto y comprador de una vez.
    ventas = Negotiation.objects.filter(vendedor=request.user).select_related('producto', 'comprador')

    return render(request, 'marketplace/mis_negociaciones.html', {
        'compras': compras,
        'ventas': ventas,
    })

@login_required
@require_POST
def finalizar_negociacion(request, neg_id, accion):
    """ Marca una venta como concretada o cancelada y descuenta el stock. """
    if accion not in {'vendido', 'cancelar'}:
        raise PermissionDenied('Acción de negociación no válida.')

    with transaction.atomic():
        neg = get_object_or_404(
            Negotiation.objects.select_for_update(),
            id=neg_id,
            vendedor=request.user,
        )
        if neg.estado != 'abierta':
            messages.info(request, 'Esta negociación ya había sido cerrada.')
            return redirect('marketplace:mis_negociaciones')

        if accion == 'vendido':
            producto = Product.objects.select_for_update().get(id=neg.producto_id)
            if producto.stock < 1:
                messages.error(request, 'No hay stock disponible para confirmar esta venta.')
                return redirect('marketplace:mis_negociaciones')
            producto.stock -= 1
            producto.es_vendido = producto.stock == 0
            producto.save(update_fields=('stock', 'es_vendido'))
            neg.estado = 'vendida'
            messages.success(request, 'Venta confirmada y stock actualizado.')
        else:
            neg.estado = 'cancelada'
            messages.info(request, 'La negociación fue cancelada.')
        neg.save(update_fields=('estado',))
    return redirect('marketplace:mis_negociaciones')

@login_required
@require_POST
def chat(request, negociacion_id):
    """ Procesa el envío de mensajes y redirige manteniendo el chat abierto. """
    neg = get_object_or_404(Negotiation, id=negociacion_id)
    if request.user not in (neg.comprador, neg.vendedor):
        raise PermissionDenied('No puedes participar en esta negociación.')

    contenido = request.POST.get('msg', '').strip()
    if neg.estado != 'abierta':
        messages.error(request, 'No puedes enviar mensajes en una negociación cerrada.')
    elif contenido:
        Message.objects.create(negociacion=neg, emisor=request.user, contenido=contenido)
    else:
        messages.error(request, 'El mensaje no puede estar vacío.')
    
    # Redirección estratégica para que el usuario no pierda el hilo visual.
    return redirect(f'/producto/{neg.producto.id}/?chat=abierto&comprador={neg.comprador.id}')
