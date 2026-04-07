from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Product, Negotiation, Message, ProductImage
from .forms import ProductForm

# --- VISTAS PÚBLICAS ---

def index(request):
    query = request.GET.get('q')
    cat_filter = request.GET.get('categoria') 
    
    productos = Product.objects.filter(stock__gt=0, esta_pausado=False)
    
    if query:
        productos = productos.filter(nombre__icontains=query) | productos.filter(descripcion__icontains=query)
    
    if cat_filter:
        productos = productos.filter(categoria=cat_filter)
        
    return render(request, 'marketplace/index.html', {
        'productos': productos, 
        'query': query,
        'cat_actual': cat_filter
    })

def product_detail(request, product_id):
    producto = get_object_or_404(Product, id=product_id)
    imagenes_extra = producto.imagenes.all() 
    return render(request, 'marketplace/product_detail.html', {
        'producto': producto,
        'imagenes_extra': imagenes_extra
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


# --- VISTAS PRIVADAS (REQUIEREN LOGIN) ---

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
                
            # CAMBIO: Redirige directo a tu perfil para ver tus publicaciones
            return redirect('/perfil/#publicaciones')
    else:
        form = ProductForm(initial={'email_contacto': request.user.email})
    return render(request, 'marketplace/vender.html', {'form': form})

# NUEVA VISTA: Para que el botón "Editar" funcione
@login_required
def editar_producto(request, product_id):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            # Si subió fotos nuevas en la edición
            images = request.FILES.getlist('extra_imgs')
            if images:
                producto.imagenes.all().delete() # Opcional: Limpia las viejas
                for img in images[:5]:
                    ProductImage.objects.create(producto=producto, imagen=img)
            return redirect('/perfil/#publicaciones')
    else:
        form = ProductForm(instance=producto)
    return render(request, 'marketplace/vender.html', {'form': form, 'editando': True})

@login_required
def iniciar_contacto(request, product_id):
    producto = get_object_or_404(Product, id=product_id)
    if producto.vendedor == request.user:
        return redirect('marketplace:index')
    neg, created = Negotiation.objects.get_or_create(
        producto=producto, comprador=request.user, vendedor=producto.vendedor
    )
    return redirect('marketplace:chat', negociacion_id=neg.id)

@login_required
def chat(request, negociacion_id):
    neg = get_object_or_404(Negotiation, id=negociacion_id)
    if request.method == 'POST':
        contenido = request.POST.get('msg')
        if contenido:
            Message.objects.create(negociacion=neg, emisor=request.user, contenido=contenido)
    mensajes = neg.mensajes.all().order_by('enviado')
    return render(request, 'marketplace/chat.html', {'neg': neg, 'mensajes': mensajes})

@login_required
def mis_negociaciones(request):
    mis_compras = Negotiation.objects.filter(comprador=request.user).order_by('-creada')
    mis_ventas = Negotiation.objects.filter(vendedor=request.user).order_by('-creada')
    return render(request, 'marketplace/mis_negociaciones.html', {'compras': mis_compras, 'ventas': mis_ventas})

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

@login_required
def pausar_producto(request, product_id):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    producto.esta_pausado = not producto.esta_pausado
    producto.save()
    return redirect('/perfil/#publicaciones')

def mensajes_pendientes(request):
    if request.user.is_authenticated:
        # Contamos negociaciones donde el último mensaje NO sea del usuario actual
        # (Para hacerlo simple: contamos negociaciones activas en las que participas)
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