#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Avg
from datetime import timedelta
import datetime, json
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Medicion
from sensor.models import Sensor
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .utils import staff_required
import jwt
from django.views.decorators.http import require_GET
from Sistema_proyecto.models import CondicionTaller,Herramienta, Alerta,OrdenTrabajo,HistorialRFID, RegistroUsoHerramienta



@require_GET
def lista_mediciones(request):
    """Devuelve las últimas 10 mediciones."""
    mediciones = Medicion.objects.all().order_by('-fecha')[:10]

    data = []
    for m in mediciones:
        try:
            sensor_nombre = Sensor.objects.get(id=m.sensor_id).nombre
        except Sensor.DoesNotExist:
            sensor_nombre = 'Desconocido'

        data.append({
            'sensor': sensor_nombre,
            'voltaje': m.voltaje,
            'corriente': m.corriente,
            'potencia': m.potencia,
            'energia': m.energia,
            'costo': m.costo,
            'fecha': m.fecha.strftime("%d/%m/%Y %H:%M:%S"),
        })

    return JsonResponse(data, safe=False)

@login_required
def informe_diario(request):

    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")

    hoy = timezone.now().date()

    if fecha_inicio:
        fecha_inicio = datetime.datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    else:
        fecha_inicio = hoy

    if fecha_fin:
        fecha_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    else:
        fecha_fin = hoy

    mediciones = Medicion.objects.filter(
        fecha__date__range=[fecha_inicio, fecha_fin]
    ).order_by('-fecha')

    total_energia = sum(m.energia for m in mediciones)

    contexto = {
        'mediciones': mediciones,
        'total_energia': round(total_energia, 3),
        'total_kwh': round(total_energia, 3),
        'desde': fecha_inicio,
        'hasta': fecha_fin,
    }
    
    return render(request, 'Sistema_proyecto/administrador/informe_diario.html', contexto)

#  API IoT - RECEPCIÓN DE DATOS DESDE ARDUINO

@csrf_exempt
def recibir_datos(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        print("📡 Datos recibidos:", data)

        # ===============================
        # 1️⃣ Validar sensor
        # ===============================
        sensor_id = data.get("sensor_id")
        if not sensor_id:
            return JsonResponse({"error": "sensor_id faltante"}, status=400)

        try:
            sensor = Sensor.objects.get(id=sensor_id)
        except Sensor.DoesNotExist:
            return JsonResponse({"error": "Sensor no existe"}, status=404)

        # ===============================
        # 2️⃣ RFID (INDEPENDIENTE DEL SENSOR)
        # ===============================
        uid = data.get("uid", "").strip().lower()
        print("🔑 UID recibido:", uid)

        if uid:
            herramienta_rfid = Herramienta.objects.filter(uid=uid).first()

            if herramienta_rfid:
                ultimo = HistorialRFID.objects.filter(
                    herramienta=herramienta_rfid
                ).order_by("-fecha").first()

                if herramienta_rfid.estado == "disponible":
                    accion = "entrada"
                    herramienta_rfid.estado = "en_uso"
                else:
                    accion = "salida"
                    herramienta_rfid.estado = "disponible"

                if not ultimo or ultimo.accion != accion:
                    HistorialRFID.objects.create(
                        herramienta=herramienta_rfid,
                        accion=accion
                    )
                    herramienta_rfid.save()
                    print(f"✅ RFID {accion.upper()} guardado")
            else:
                print("⚠️ UID no asociado a herramienta")

        # ===============================
        # 3️⃣ Preparar datos del sensor
        # ===============================
        herramienta_sensor = Herramienta.objects.filter(sensor=sensor).first()

        temperatura = float(data.get("temperatura", 0))
        humedad     = float(data.get("humedad", 0))
        vibracion   = float(data.get("vibracion", 0))
        corriente   = float(data.get("corriente", 0))
        voltaje     = float(data.get("voltaje", 220))
        potencia    = float(data.get("potencia", corriente * voltaje))
        energia     = float(data.get("energia", 0))
        ssid        = data.get("ssid")
        bssid       = data.get("bssid")

        # ===============================
        # 4️⃣ Buscar OT activa ANTES de crear medición
        # ===============================
        ot_real = None
        if herramienta_sensor:
            ot_real = OrdenTrabajo.objects.filter(
                herramientas=herramienta_sensor,
                estado="en_proceso"
            ).first()

        # ===============================
        # 5️⃣ Calcular costo acumulado del día
        # ===============================
        energia_hoy = Medicion.objects.filter(
            sensor=sensor,
            fecha__date=timezone.now().date()
        ).aggregate(Sum('energia'))['energia__sum'] or 0

        energia_total_hoy = float(energia_hoy) + energia
        costo_acumulado   = int(round(energia_total_hoy * 160, 2))

        # ===============================
        # 6️⃣ Guardar medición con OT ya definida
        # ===============================
        Medicion.objects.create(
            sensor=sensor,
            herramienta=herramienta_sensor,
            orden_trabajo=ot_real,
            temperatura=temperatura,
            humedad=humedad,
            vibracion=vibracion,
            corriente=corriente,
            voltaje=voltaje,
            potencia=potencia,
            energia=energia,
            costo=costo_acumulado,
            ssid=ssid,
            bssid=bssid
        )

        # ===============================
        # 7️⃣ Acumular energía en OT real
        # ===============================
        if ot_real:
            RegistroUsoHerramienta.objects.create(
                orden_trabajo=ot_real,
                herramienta=herramienta_sensor,
                energia_consumida=energia
            )

        # ===============================
        # 8️⃣ Guardar condición taller cada 10 min
        # ===============================
        ahora = timezone.now()
        ultima_condicion = CondicionTaller.objects.order_by("-fecha").first()

        guardar = False
        if not ultima_condicion:
            guardar = True
        else:
            delta = (ahora - ultima_condicion.fecha).total_seconds()
            if delta >= 600:
                guardar = True

        if guardar:
            CondicionTaller.objects.create(
                temperatura=temperatura,
                humedad=humedad,
                vibracion=vibracion
            )

        return JsonResponse({
            "status": "ok",
            "message": "RFID e IoT procesados correctamente"
        })

    except Exception as e:
        print("❌ Error real en recibir_datos:", e)
        return JsonResponse(
            {"status": "error", "message": str(e)},
            status=500
        )
    


def procesar_rfid(uid):
    try:
        herramienta = Herramienta.objects.get(uid=uid)
    except Herramienta.DoesNotExist:
        return {"status": "error", "message": "UID no registrado"}

    ahora = timezone.now()

    # ¿La herramienta está siendo usada?
    if herramienta.estado != "en_uso":
        # Registrar ENTRADA
        HistorialRFID.objects.create(
            herramienta=herramienta,
            accion="entrada"
        )
        herramienta.estado = "en_uso"
        herramienta.save()
        return {"status": "ok", "accion": "entrada"}

    else:
        # Registrar SALIDA
        HistorialRFID.objects.create(
            herramienta=herramienta,
            accion="salida"
        )
        herramienta.estado = "disponible"
        herramienta.save()
        return {"status": "ok", "accion": "salida"}
 

#  GENERADOR DE URL PARA METABASE

def _mb_url(resource_type: str, resource_id: int, params=None):
    site = getattr(settings, "METABASE_SITE_URL", None)
    secret = getattr(settings, "METABASE_EMBEDDING_SECRET", None)

    if not (site and secret and resource_id):
        return None

    payload = {
        "resource": {resource_type: resource_id},
        "params": params or {},
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    }

    token = jwt.encode(payload, secret, algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode("utf-8")

    path = "dashboard" if resource_type == "dashboard" else "question"
    return f"{site}/embed/{path}/{token}#bordered=true&titled=true"



#  PÁGINAS HTML DE VISUALIZACIÓN


@csrf_exempt

def ultimas_mediciones(request):
    mediciones = Medicion.objects.all().order_by('-id')[:5]

    data = [{
        'id': m.id,
        'sensor': str(m.sensor),
        'voltaje': m.voltaje,
        'corriente': m.corriente,
        'potencia': m.potencia,
        'fecha': m.fecha.strftime('%Y-%m-%d %H:%M:%S')
    } for m in mediciones]

    return JsonResponse({'mediciones': data}, safe=False)






def metabase_diag(request):
    site = getattr(settings, "METABASE_SITE_URL", "")
    secret = getattr(settings, "METABASE_EMBEDDING_SECRET", "")
    dashid = getattr(settings, "METABASE_DASHBOARD_ID", 0)

    url = _mb_url("dashboard", dashid, {})

    return JsonResponse({
        "METABASE_SITE_URL": site,
        "SECRET_len": len(secret),
        "DASHBOARD_ID": dashid,
        "generated_url": url,
    })


def pagina_mediciones(request):
    user = request.user
    if user.is_anonymous:
        return HttpResponseForbidden("No autorizado")
    rol = getattr(user, "rol", None)
    if not user.is_staff and rol != "admin":
        return HttpResponseForbidden("No autorizado")
    iframeUrl = "http://127.0.0.1:3000/public/dashboard/85fcc709-a782-43b4-84d6-f0a8f7acf0b3"
    return render(request, "Sistema_proyecto/administrador/mediciones.html", {
        "metabase_iframe_url": iframeUrl
    })


def resumen_mensual(request):
    """
    Entrega la energía y el costo total del mes actual.
    Además separa por sensores (SCT1, SCT2, etc.).
    """

    
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    
    mediciones_mes = Medicion.objects.filter(fecha__gte=inicio_mes)

    
    total_energia = mediciones_mes.aggregate(Sum("energia"))["energia__sum"] or 0
    total_costo = mediciones_mes.aggregate(Sum("costo"))["costo__sum"] or 0

    
    sensores = Sensor.objects.all()
    detalle_sensores = []

    for sensor in sensores:
        consumo_sensor = mediciones_mes.filter(sensor=sensor).aggregate(
            Sum("energia"), Sum("costo")
        )

        detalle_sensores.append({
            "sensor": sensor.nombre,
            "energia": consumo_sensor["energia__sum"] or 0,
            "costo": consumo_sensor["costo__sum"] or 0,
        })

    contexto = {
        "inicio_mes": inicio_mes,
        "total_energia": round(total_energia, 4),
        "total_kwh": round(total_energia, 4),
        "total_costo": total_costo,
        "detalle_sensores": detalle_sensores,
    }

    return render(request, "Sistema_proyecto/administrador/resumen_mensual.html", contexto)


def mediciones_del_dia(request):
    hoy = timezone.localtime().date()

    mediciones = Medicion.objects.filter(
        fecha__date=hoy
    ).order_by('-fecha')

    data = [{
        "fecha": m.fecha.strftime("%d/%m/%Y %H:%M"),
        "sensor": m.sensor.nombre,
        "corriente": m.corriente,
        "voltaje": m.voltaje,
        "potencia": m.potencia,
        "energia": m.energia,
        "costo": m.costo,
    } for m in mediciones]

    return JsonResponse({"mediciones": data})
