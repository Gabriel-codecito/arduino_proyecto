#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.apps import AppConfig

class MedicionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mediciones'

    def ready(self):
        import mediciones.signals
