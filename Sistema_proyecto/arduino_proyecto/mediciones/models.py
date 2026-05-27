#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025




from django.db import models
from django.utils import timezone
from Sistema_proyecto.models import OrdenTrabajo
from django.db.models import Avg
# Create your models here.



class Medicion(models.Model):
    sensor = models.ForeignKey('sensor.Sensor', on_delete=models.CASCADE, related_name='mediciones')
    vibracion = models.FloatField(default=0)
    temperatura = models.FloatField(null=True, blank=True, default=0)
    humedad = models.FloatField(null=True, blank=True, default=0)
    voltaje = models.FloatField(default=0)
    corriente = models.FloatField(default=0)
    potencia = models.FloatField(default=0)
    energia = models.FloatField(default=0)
    costo = models.DecimalField(default=0, decimal_places=4, max_digits=10)
    factor_potencia = models.FloatField(default=1)
    frecuencia = models.FloatField(default=50)
    fecha = models.DateTimeField(auto_now_add=True)
    herramienta = models.ForeignKey('Sistema_proyecto.Herramienta', on_delete=models.SET_NULL, null=True, blank=True)
    orden_trabajo = models.ForeignKey('Sistema_proyecto.OrdenTrabajo', on_delete=models.SET_NULL, null=True, blank=True)  # ✅ correcto
    ssid = models.CharField(max_length=100, null=True, blank=True)
    bssid = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'Sistema_proyecto_medicion'

    def save(self, *args, **kwargs):
        self.potencia = round(self.voltaje * self.corriente * self.factor_potencia, 2)
        TARIFA_CLP = 160
        self.energia = round((self.potencia * 20) / (1000 * 3600), 6)
        self.costo = round(self.energia * 160, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sensor} - {self.fecha:%Y-%m-%d %H:%M}"
    

class MedicionResumen(models.Model):
    costo = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.costo} - {self.fecha}"
    
class RegistroRFID(models.Model):
    uid = models.CharField(max_length=50)
    temperatura = models.FloatField()
    humedad = models.FloatField()
    vibracion = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"UID {self.uid} - {self.fecha}"