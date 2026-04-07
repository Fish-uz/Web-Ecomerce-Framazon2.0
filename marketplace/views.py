from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Product, Negotiation, Message, ProductImage
from .forms import ProductForm

# --- VISTAS PÚBLICAS ---

def index(request):
    query = request.GET.get('q')
    cat_filter = request.GET.get('categoria') # Capturamos la categoría de la URL
    
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
    # Obtenemos las imágenes de la galería para el carrusel/detalles
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
    
    # Compras que yo hice y que ya se cerraron
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

            # Lógica para guardar las fotos múltiples de la galería
            images = request.FILES.getlist('extra_imgs')
            for img in images[:5]: # Límite de 5 fotos
                ProductImage.objects.create(producto=nuevo_prod, imagen=img)
                
            return redirect('marketplace:perfil')
    else:
        # Pre-llenamos datos de contacto si existen
        form = ProductForm(initial={
            'email_contacto': request.user.email,
        })
    return render(request, 'marketplace/vender.html', {'form': form})

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
    # Unificamos la vista de Compra / Venta
    mis_compras = Negotiation.objects.filter(comprador=request.user).order_by('-creada')
    mis_ventas = Negotiation.objects.filter(vendedor=request.user).order_by('-creada')
    
    return render(request, 'marketplace/mis_negociaciones.html', {
        'compras': mis_compras,
        'ventas': mis_ventas
    })

@login_required
def finalizar_negociacion(request, neg_id, accion):
    # Buscamos la negociación donde el usuario actual es el vendedor
    neg = get_object_or_404(Negotiation, id=neg_id, vendedor=request.user)
    producto = neg.producto

    if accion == 'vendido':
        neg.estado = 'vendida'
        # Verificamos que haya stock antes de descontar
        if producto.stock > 0:
            producto.stock -= 1  # Aquí descontamos 1 unidad por venta
            
            # Si se acabó el stock, marcamos el producto como vendido globalmente
            if producto.stock == 0:
                producto.es_vendido = True
            
            producto.save()
    else:
        neg.estado = 'cancelada'
    
    neg.save()
    # Redirigimos a la pestaña de Mis Ventas para ver el cambio
    return redirect('marketplace:mis_negociaciones')

@login_required
def cambiar_estado_producto(request, product_id, accion):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    
    if accion == 'pausar':
        producto.esta_pausado = not producto.esta_pausado # Si está activo lo pausa, y viceversa
    elif accion == 'vendido':
        if producto.stock > 0:
            producto.stock -= 1 # Baja el stock en 1
            if producto.stock == 0:
                producto.es_vendido = True
    
    producto.save()
    return redirect('marketplace:perfil')

@login_required
def pausar_producto(request, product_id):
    producto = get_object_or_404(Product, id=product_id, vendedor=request.user)
    # Cambia de True a False o viceversa
    producto.esta_pausado = not producto.esta_pausado
    producto.save()
    return redirect('marketplace:perfil')