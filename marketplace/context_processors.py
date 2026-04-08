# ==============================================================================
# FUNCIÓN DE NOTIFICACIONES GLOBALES
# ==============================================================================
def mensajes_pendientes(request):
    """
    Calcula el número de negociaciones activas para mostrar notificaciones 
    en el icono de 'Compra / Venta' de la Navbar.
    """
    
    # 1. VERIFICACIÓN DE SESIÓN:
    # Solo intentamos contar mensajes si el usuario ha iniciado sesión.
    if request.user.is_authenticated:
        
        # 2. LÓGICA DE CONTEO (COMPRADOR + VENDEDOR):
        # Filtramos las negociaciones que están en estado 'en_progreso'.
        
        # Parte A: Contamos las negociaciones donde el usuario es el COMPRADOR.
        compras_activas = Negotiation.objects.filter(
            estado='en_progreso', 
            comprador=request.user
        ).count()
        
        # Parte B: Contamos las negociaciones donde el usuario es el VENDEDOR.
        ventas_activas = Negotiation.objects.filter(
            estado='en_progreso', 
            vendedor=request.user
        ).count()
        
        # 3. SUMA TOTAL:
        # Combinamos ambos conteos para obtener el número total de chats pendientes.
        count = compras_activas + ventas_activas
        
        # 4. RETORNO DE DATOS:
        # Devolvemos un diccionario. La clave 'notificaciones_chat' es la que 
        # usarás en el HTML como {{ notificaciones_chat }}.
        return {'notificaciones_chat': count}

    # 5. CASO PARA USUARIOS NO LOGUEADOS:
    # Si el usuario es un visitante anónimo, el contador siempre será 0.
    return {'notificaciones_chat': 0}