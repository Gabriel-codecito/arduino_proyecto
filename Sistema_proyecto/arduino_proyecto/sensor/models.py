#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025




from django.db import models
from django.utils import timezone
from datetime import timedelta


class Sensor(models.Model):
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'En Mantenimiento'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=50, default='SCT-013')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='inactivo')
    fecha_instalacion = models.DateField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    ubicacion_fija = models.CharField(max_length=100, default='Taller Principal',  editable=False)
    ultima_medicion = models.DateTimeField(null=True, blank=True)

    
    
    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        db_table = 'sensor_sensor'
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'

def actualizar_estados_sensores():
    ahora = timezone.now()
    limite_mantenimiento = ahora - timedelta(seconds=60)
    limite_inactivo = ahora - timedelta(seconds=10)

    for sensor in Sensor.objects.all():
        ultima = sensor.mediciones.order_by('-fecha').first()

        if not ultima:
            sensor.estado = 'inactivo'

        else:
            if ultima.fecha < limite_mantenimiento:
                sensor.estado = 'mantenimiento'
            elif ultima.fecha < limite_inactivo:
                sensor.estado = 'inactivo'
            else:
                sensor.estado = 'activo'

        sensor.save()