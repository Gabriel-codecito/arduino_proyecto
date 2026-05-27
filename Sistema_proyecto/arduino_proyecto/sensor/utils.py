#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.shortcuts import redirect
from django.http import HttpResponseForbidden,HttpResponseRedirect

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):

        # NO autenticado → redirigir
        if not request.user.is_authenticated:
            return redirect("/login/")

        # Autenticado pero NO staff → 403
        if not request.user.is_staff:
            return HttpResponseForbidden("No tienes permisos")

        # Staff → OK
        return view_func(request, *args, **kwargs)

    return wrapper

