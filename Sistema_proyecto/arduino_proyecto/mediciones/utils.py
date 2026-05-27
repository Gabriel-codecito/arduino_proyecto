#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.http import HttpResponseForbidden
from django.shortcuts import redirect



def staff_required(view_func):
    def wrapper(request, *args, **kwargs):

        # Caso 1: Usuario NO autenticado
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Debe iniciar sesión")

        # Caso 2: Usuario autenticado pero NO staff
        if not request.user.is_staff:
            return HttpResponseForbidden("se requiere staff")

        # Caso 3: Usuario staff → permitir acceso
        return view_func(request, *args, **kwargs)

    return wrapper
