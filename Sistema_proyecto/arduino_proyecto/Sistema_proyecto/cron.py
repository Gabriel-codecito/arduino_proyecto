#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


import os
import datetime
from django.conf import settings
from openpyxl import Workbook
from mediciones.models import Medicion

def limpiar_y_respaldar_mediciones():
    """
    Genera un respaldo en Excel y limpia la tabla Medicion.
    """
    hoy = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_archivo = f"respaldo_mediciones_{hoy}.xlsx"
    ruta_respaldo = os.path.join(settings.BASE_DIR, "respaldos")
    if not os.path.exists(ruta_respaldo):
        os.makedirs(ruta_respaldo)
    archivo_final = os.path.join(ruta_respaldo, nombre_archivo)
    wb = Workbook()
    ws = wb.active
    ws.title = "Mediciones"
    ws.append(["Fecha", "Potencia", "Voltaje", "Corriente", "Sensor"])
    mediciones = Medicion.objects.all()
    for m in mediciones:
        ws.append([
            m.fecha.strftime("%Y-%m-%d %H:%M"),
            m.potencia,
            m.voltaje,
            m.corriente,
            str(m.sensor)
        ])
    wb.save(archivo_final)
    cantidad = mediciones.count()
    mediciones.delete()
    print(f"[CRON] {cantidad} mediciones respaldadas y eliminadas.")
