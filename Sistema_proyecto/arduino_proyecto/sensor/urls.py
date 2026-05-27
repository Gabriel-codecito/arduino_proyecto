#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.urls import path
from . import views

urlpatterns = [
    path('sensores/', views.pagina_sensores, name='sensores'),
    path('sensor/<int:pk>/estado/', views.cambiar_estado_sensor, name='cambiar_estado_sensor'),
]
