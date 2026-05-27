#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.db.models.signals import post_save
from django.dispatch import receiver
from mediciones.models import Medicion
from Sistema_proyecto.models import OrdenTrabajo, RegistroUsoHerramienta, ComentarioOT
from django.utils import timezone

@receiver(post_save, sender=Medicion)
def procesar_medicion_iot(sender, instance, created, **kwargs):
    if not created:
        return

    herramienta = instance.herramienta
    if not herramienta:
        return

    # 1️⃣ Buscar OT activa para esa herramienta
    ot = OrdenTrabajo.objects.filter(
        herramientas=herramienta,
        estado__in=["asignada", "en_proceso"]
    ).order_by("-fecha_creacion").first()

    if not ot:
        return

    # 2️⃣ Crear o actualizar el registro de uso
    registro, reg_created = RegistroUsoHerramienta.objects.get_or_create(
        herramienta=herramienta,
        orden_trabajo=ot,
        defaults={"fecha_inicio": timezone.now()}
    )

    # 3️⃣ Sumar energía automáticamente
    registro.energia_consumida += instance.energia
    registro.save()

    # 4️⃣ Actualizar energía total de la OT
    ot.energia_total_kwh += instance.energia
    ot.save()

    # 5️⃣ Detectar vibración peligrosa
    if instance.vibracion > 80:  
        ComentarioOT.objects.create(
            orden=ot,
            comentario=f"⚠ Vibración elevada detectada: {instance.vibracion}."
        )

    # 6️⃣ Detectar sobrecalentamiento
    if instance.temperatura and instance.temperatura > 70:
        ComentarioOT.objects.create(
            orden=ot,
            comentario=f"🔥 Sobrecalentamiento detectado: {instance.temperatura}°C."
        )
