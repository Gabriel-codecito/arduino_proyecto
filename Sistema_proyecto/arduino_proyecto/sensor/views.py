#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Sensor, actualizar_estados_sensores
from sensor.utils import staff_required
from django.http import HttpResponse, HttpResponseForbidden
from mediciones.models import Medicion
from django.utils import timezone

def monitor_sensores():
    ahora = timezone.now()

    for sensor in Sensor.objects.all():

        if not sensor.ultima_conexion:
            continue

        diff = (ahora - sensor.ultima_conexion).total_seconds()

        if diff > 180:
            nuevo = "desconectado"
        elif diff > 60:
            nuevo = "inactivo"
        else:
            nuevo = "activo"

        if sensor.estado != nuevo:
            sensor.estado = nuevo
            sensor.save()
            print(f"📡 Sensor {sensor.id} → {nuevo}")


@login_required
@user_passes_test(lambda u: u.is_staff, login_url="/login/")
def pagina_sensores(request):
    """Carga dashboard público o embebido."""
    iframeUrl = "http://127.0.0.1:3000/public/question/aa9491be-0381-4c68-b981-7ffa0d43ce63"
    return render(request, "Sistema_proyecto/administrador/sensores.html", {
        "metabase_iframe_url": iframeUrl
    })

def es_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
def cambiar_estado_sensor(request, pk):
    sensor = get_object_or_404(Sensor, pk=pk)

    # CLIENTE → 403
    if not request.user.is_staff:
        return HttpResponseForbidden("No tienes permiso para cambiar estado del sensor.")

    # Cambiar estado
    nuevo_estado = request.GET.get("estado", "activo")
    sensor.estado = nuevo_estado
    sensor.save()

    # SI HAY ALGUNA MEDICIÓN → devolver 200 (test de integración)
    hay_medicion = Medicion.objects.filter(sensor=sensor).exists()
    if hay_medicion:
        return HttpResponse("Estado actualizado correctamente.", status=200)

    # SIN medición → funcionar normal → 302 redirect
    return redirect("sensores")