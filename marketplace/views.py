from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator
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
    productos_list = Product.objects.filter(stock__gt=0, esta_pausado=False).order_by('-id')
    
    if query:
        # Filtra por nombre o descripción usando el operador OR (|).
        productos_list = productos_list.filter(nombre__icontains=query) | productos_list.filter(descripcion__icontains=query)
    
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
    
    mensajes = None
    if request.user.is_authenticated:
        # Identificamos quién está viendo la página para cargar el chat correcto.
        comprador_id = request.GET.get('comprador')
        
        if producto.vendedor == request.user:
            # LÓGICA VENDEDOR: Si viene de 'Atender', carga el chat con ese comprador específico.
            if comprador_id:
                negociacion = Negotiation.objects.filter(producto=producto, comprador_id=comprador_id).first()
            else:
                # Si no, carga la conversación más reciente de este producto.
                negociacion = Negotiation.objects.filter(producto=producto).order_by('-creada').first()
        else:
            # LÓGICA COMPRADOR: Carga su propia conversación con el dueño del producto.
            negociacion = Negotiation.objects.filter(producto=producto, comprador=request.user).first()

        if negociacion:
            mensajes = negociacion.mensajes.all().order_by('enviado')

    return render(request, 'marketplace/product_detail.html', {
        'producto': producto,
        'imagenes_extra': imagenes_extra,
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
    compras_finalizadas = Negotiation.objects.filter(comprador=request.user, estado='vendida')
    
    return render(request, 'marketplace/perfil.html', {
        'mis_productos': mis_productos,
        'compras_finalizadas': compras_finalizadas,
        'count_compras': compras_finalizadas.count(),
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
def iniciar_contacto(request, product_id):
    """ Crea el vínculo inicial entre comprador y vendedor. """
    producto = get_object_or_404(Product, id=product_id)
    
    if producto.vendedor == request.user:
        return redirect('marketplace:product_detail', product_id=producto.id)

    # Crea la negociación si no existe o recupera la actual.
    negociacion, created = Negotiation.objects.get_or_create(
        producto=producto,
        comprador=request.user,
        vendedor=producto.vendedor
    )

    if request.method == 'POST':
        msg_contenido = request.POST.get('msg')
        if msg_contenido:
            Message.objects.create(negociacion=negociacion, emisor=request.user, contenido=msg_contenido)
    
    return redirect(f'/producto/{producto.id}/?chat=abierto')

@login_required
def mis_negociaciones(request):
    """ Lista todas las conversaciones donde el usuario compra o vende. """
    compras = Negotiation.objects.filter(comprador=request.user).order_by('-creada')
    # select_related optimiza la consulta para obtener datos del producto y comprador de una vez.
    ventas = Negotiation.objects.filter(producto__vendedor=request.user).select_related('producto', 'comprador').order_by('-creada')

    return render(request, 'marketplace/mis_negociaciones.html', {
        'compras': compras,
        'ventas': ventas,
    })

@login_required
def finalizar_negociacion(request, neg_id, accion):
    """ Marca una venta como concretada o cancelada y descuenta el stock. """
    neg = get_object_or_404(Negotiation, id=neg_id, vendedor=request.user)
    producto = neg.producto
    if accion == 'vendido':
        neg.estado = 'vendida'
        if producto.stock > 0:
            producto.stock -= 1
            if producto.stock == 0:
                producto.es_vendido = True
            producto.save()
    else:
        neg.estado = 'cancelada'
    neg.save()
    return redirect('marketplace:mis_negociaciones')

@login_required
def chat(request, negociacion_id):
    """ Procesa el envío de mensajes y redirige manteniendo el chat abierto. """
    neg = get_object_or_404(Negotiation, id=negociacion_id)
    if request.method == 'POST':
        contenido = request.POST.get('msg')
        if contenido:
            Message.objects.create(negociacion=neg, emisor=request.user, contenido=contenido)
    
    # Redirección estratégica para que el usuario no pierda el hilo visual.
    return redirect(f'/producto/{neg.producto.id}/?chat=abierto&comprador={neg.comprador.id}')

# ==============================================================================
# 4. PROCESADORES GLOBALES (PARA NAVBAR)
# ==============================================================================

def mensajes_pendientes(request):
    """ Inyecta el contador de notificaciones de chat en todas las páginas. """
    if request.user.is_authenticated:
        count = Negotiation.objects.filter(estado='en_progreso', comprador=request.user).count() + \
                Negotiation.objects.filter(estado='en_progreso', vendedor=request.user).count()
        return {'notificaciones_chat': count}
    return {'notificaciones_chat': 0}