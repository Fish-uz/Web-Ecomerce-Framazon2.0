from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Negotiation, Message, ProductImage
from .forms import ProductForm

# --- VISTAS PÚBLICAS ---

def index(request):
    query = request.GET.get('q')
    cat_filter = request.GET.get('categoria') 
    
    productos_list = Product.objects.filter(stock__gt=0, esta_pausado=False).order_by('-id')
    
    if query:
        productos_list = productos_list.filter(nombre__icontains=query) | productos_list.filter(descripcion__icontains=query)
    
    if cat_filter:
        productos_list = productos_list.filter(categoria=cat_filter)
    
    paginator = Paginator(productos_list, 12)
    page_number = request.GET.get('page')
    productos = paginator.get_page(page_number)
        
    return render(request, 'marketplace/index.html', {
        'productos': productos, 
        'query': query,
        'cat_actual': cat_filter
    })

def product_detail(request, product_id):
    producto = get_object_or_404(Product, id=product_id)
    imagenes_extra = producto.imagenes.all() 
    
    mensajes = None
    if request.user.is_authenticated:
        # 1. Intentamos obtener el ID del comprador desde la URL (enviado por el botón "Atender")
        comprador_id = request.GET.get('comprador')
        
        if producto.vendedor == request.user:
            # LÓGICA VENDEDOR: Si existe un comprador_id en la URL, filtramos por él
            if comprador_id:
                negociacion = Negotiation.objects.filter(producto=producto, comprador_id=comprador_id).first()
            else:
                # Si no hay ID en la URL, mostramos la negociación más reciente de este producto
                negociacion = Negotiation.objects.filter(producto=producto).order_by('-creada').first()
        else:
            # LÓGICA COMPRADOR: Mantenemos tu estructura original
            negociacion = Negotiation.objects.filter(
                producto=producto, 
                comprador=request.user
            ).first()

        if negociacion:
            mensajes = negociacion.mensajes.all().order_by('enviado')

    return render(request, 'marketplace/product_detail.html', {
        'producto': producto,
        'imagenes_extra': imagenes_extra,
        'mensajes': mensajes,
    })

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('marketplace:index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registro.html', {'form': form})


# --- GESTIÓN DE PERFIL Y PRODUCTOS (PRIVADAS) ---

@login_required
def perfil(request):
    mis_productos = Product.objects.filter(vendedor=request.user)
    compras_finalizadas = Negotiation.objects.filter(comprador=request.user, estado='vendida')
    
    return render(request, 'marketplace/perfil.html', {
        'mis_productos': mis_productos,
        'compras_finalizadas': compras_finalizadas,
        'count_compras': compras_finalizadas.count(),
    })

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_prod = form.save(commit=False)
            nuevo_prod.vendedor = request.user
            nuevo_prod.save()

            images = request.FILES.getlist('extra_imgs')
            for img in images[:5]:
                ProductImage.objects.create(producto=nuevo_prod, imagen=img)
                
            return redirect('/perfil/#publicaciones')
    else:
        form = ProductForm(initial={'email_contacto': request.user.email})
    return render(request, 'marketplace/vender.html', {'form': form})

@login_required
def editar_producto(request, product_id):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            images = request.FILES.getlist('extra_imgs')
            if images:
                producto.imagenes.all().delete()
                for img in images[:5]:
                    ProductImage.objects.create(producto=producto, imagen=img)
            return redirect('/perfil/#publicaciones')
    else:
        form = ProductForm(instance=producto)
    return render(request, 'marketplace/vender.html', {'form': form, 'editando': True})

@login_required
def pausar_producto(request, product_id):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    producto.esta_pausado = not producto.esta_pausado
    producto.save()
    return redirect('/perfil/#publicaciones')

@login_required
def cambiar_estado_producto(request, product_id, accion):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    if accion == 'pausar':
        producto.esta_pausado = not producto.esta_pausado
    elif accion == 'vendido':
        if producto.stock > 0:
            producto.stock -= 1
            if producto.stock == 0:
                producto.es_vendido = True
    producto.save()
    return redirect('marketplace:perfil')


# --- FLUJO DE NEGOCIACIÓN Y CHAT ---

@login_required
def iniciar_contacto(request, product_id):
    producto = get_object_or_404(Product, id=product_id)
    
    # Evitar que el vendedor se interese en su propio producto
    if producto.vendedor == request.user:
        return redirect('marketplace:product_detail', product_id=producto.id)

    # Buscar si ya existe la negociación o crear una nueva
    negociacion, created = Negotiation.objects.get_or_create(
        producto=producto,
        comprador=request.user,
        vendedor=producto.vendedor # ¡Muy importante que este campo se guarde!
    )

    if request.method == 'POST':
        msg_contenido = request.POST.get('msg')
        if msg_contenido:
            Message.objects.create(
                negociacion=negociacion,
                emisor=request.user,
                contenido=msg_contenido
            )
    
    return redirect(f'/producto/{producto.id}/?chat=abierto')

@login_required
def mis_negociaciones(request):
    # 1. Compras: Negociaciones donde yo soy el comprador
    compras = Negotiation.objects.filter(comprador=request.user).order_by('-creada')
    
    # 2. Ventas: Negociaciones donde yo soy el vendedor de los productos
    # Usamos select_related para que cargue rápido los datos del producto y comprador
    ventas = Negotiation.objects.filter(producto__vendedor=request.user).select_related('producto', 'comprador').order_by('-creada')

    return render(request, 'marketplace/mis_negociaciones.html', {
        'compras': compras,
        'ventas': ventas,
    })

@login_required
def finalizar_negociacion(request, neg_id, accion):
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
    neg = get_object_or_404(Negotiation, id=negociacion_id)
    if request.method == 'POST':
        contenido = request.POST.get('msg')
        if contenido:
            # Guarda el mensaje en la base de datos
            Message.objects.create(negociacion=neg, emisor=request.user, contenido=contenido)
    
    # En lugar de buscar un template 'chat.html' que no existe, 
    # te redirige al detalle del producto manteniendo el chat visible.
    return redirect(f'/producto/{neg.producto.id}/?chat=abierto&comprador={neg.comprador.id}')


# --- PROCESADORES DE CONTEXTO / NOTIFICACIONES ---

def mensajes_pendientes(request):
    if request.user.is_authenticated:
        count = Negotiation.objects.filter(
            estado='en_progreso'
        ).filter(
            comprador=request.user
        ).count() + Negotiation.objects.filter(
            estado='en_progreso'
        ).filter(
            vendedor=request.user
        ).count()
        
        return {'notificaciones_chat': count}
    return {'notificaciones_chat': 0}