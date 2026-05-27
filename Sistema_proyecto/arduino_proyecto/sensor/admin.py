#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.contrib import admin
from .models import Sensor

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "estado")

    def herramienta_asociada(self, obj):
        return obj.herramienta.nombre if hasattr(obj, "herramienta") and obj.herramienta else "—"