#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.urls import path
from . import views


urlpatterns = [
    path('api/recibir-datos/', views.recibir_datos, name='recibir_datos'),
    path('api/lista-mediciones/', views.lista_mediciones, name='api_lista_mediciones'),
    path('api/ultimas-mediciones/', views.ultimas_mediciones, name='api_ultimas_mediciones'),
    path('informes/diario/', views.informe_diario, name='informe_diario'),
    path('informes/mensual/', views.resumen_mensual, name='resumen_mensual'),
    path('mediciones/pagina/', views.pagina_mediciones, name='pagina_mediciones'),
    path('metabase/diagnostico/', views.metabase_diag, name='metabase_diag'),
    path('mediciones/mediciones-dia/', views.mediciones_del_dia, name='mediciones_dia'),


]