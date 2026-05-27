#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from .models import Herramienta, HistorialRFID, Alerta
from django.contrib import admin


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "estado")



@admin.register(HistorialRFID)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ("herramienta", "accion", "fecha")
    list_filter = ("accion", "fecha")

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ("herramienta", "tipo", "mensaje", "fecha")
    list_filter = ("tipo", "fecha")