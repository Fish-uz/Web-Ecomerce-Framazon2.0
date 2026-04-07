# marketplace/views.py o context_processors.py

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