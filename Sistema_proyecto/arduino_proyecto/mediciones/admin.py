#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.contrib import admin
from .models import Medicion, MedicionResumen


@admin.register(Medicion)
class MedicionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "sensor", "temperatura", "humedad", "vibracion",
        "corriente", "voltaje", "potencia", "energia",
        "costo", "fecha", "herramienta"
    )
    list_filter = ("sensor", "fecha")
    search_fields = ("sensor__nombre",)

@admin.register(MedicionResumen)
class MedicionResumenAdmin(admin.ModelAdmin):
    list_display = ("id", "costo", "fecha")
    list_filter = ("fecha",)
