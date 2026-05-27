#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.db.models.signals import post_save
from django.dispatch import receiver
from models import CondicionTaller

@receiver(post_save, sender=CondicionTaller)
def evaluar_alerta(sender, instance, **kwargs):
    if instance.corriente and instance.corriente > 8:
        instance.alerta = True
        instance.tipo_alerta = "Sobreconsumo"
        instance.detalle_alerta = "La herramienta está consumiendo más energía de lo normal."
        instance.save()

    if instance.vibracion > 900:
        instance.alerta = True
        instance.tipo_alerta = "Vibración peligrosa"
        instance.detalle_alerta = "Puede indicar falla mecánica."
        instance.save()
