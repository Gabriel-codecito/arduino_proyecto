#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from mediciones.models import Medicion


def validar_rut(rut, dv):
    rut = str(rut).replace(".", "").replace("-", "")
    dv = dv.upper()

    if not rut.isdigit():
        return False

    if len(rut) < 7 or len(rut) > 8:
        return False

    suma = 0
    multiplicador = 2

    for d in reversed(rut):
        suma += int(d) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2

    resto = suma % 11
    dv_real = 11 - resto

    if dv_real == 11:
        dv_real = "0"
    elif dv_real == 10:
        dv_real = "K"
    else:
        dv_real = str(dv_real)

    return dv_real == dv




def staff_required(view_func):
    def wrapper(request, *args, **kwargs):

        # 1) Usuario NO autenticado → 403 con texto correcto
        if not request.user.is_authenticated:
            return HttpResponseForbidden("se requiere staff")

        # 2) Usuario autenticado pero NO staff → 403 con texto correcto
        if not request.user.is_staff:
            return HttpResponseForbidden("se requiere staff")

        # 3) Usuario staff → puede continuar
        return view_func(request, *args, **kwargs)

    return wrapper
def admin_required_redirect(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if not request.user.is_staff:
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper

def enviar_notificacion_cotizacion(cotizacion, estado):
    estado_lower = estado.lower() 

    asunto = f"Actualización de tu cotización #{cotizacion.id}"

    template = render_to_string(
        "Sistema_proyecto/administrador/notificacion_cotizacion.html",
        {
            "nombre": cotizacion.nombre,
            "servicio": cotizacion.servicio,
            "estado": estado_lower,
            "id": cotizacion.id,
        }
    )

    email = EmailMessage(
        subject=asunto,
        body=template,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[cotizacion.correo],
    )

    email.content_subtype = "html"
    email.send()


def enviar_presupuesto_email(presupuesto):
    aceptar_url = f"{settings.SITE_URL}/presupuestos/{presupuesto.id}/aceptar/"
    rechazar_url = f"{settings.SITE_URL}/presupuestos/{presupuesto.id}/rechazar/"

    html = render_to_string(
        'Sistema_proyecto/presupuestos/email_presupuesto.html',
        {
            "presupuesto": presupuesto,
            "aceptar_url": aceptar_url,
            "rechazar_url": rechazar_url,
        }
    )

    correo_cliente = presupuesto.cotizacion.correo

    email = EmailMessage(
        subject=f"Presupuesto #{presupuesto.id} - PU Ingenierías",
        body=html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[correo_cliente],
    )
    email.content_subtype = "html"
    email.send()

def calcular_costo_energia(herramienta, tarifa_kw=160):
    """
    Calcula energía total y costo según mediciones asociadas a la herramienta.
    """

    # Obtener todas las mediciones que tienen asignada esta herramienta
    mediciones = Medicion.objects.filter(herramienta=herramienta)

    # Sumar toda la energía
    energia_total = sum(m.energia for m in mediciones)

    # Calcular costo
    costo_estimado = round(energia_total * tarifa_kw, 2)

    return energia_total, costo_estimado


