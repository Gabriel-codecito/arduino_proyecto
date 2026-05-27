#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from datetime import date
from django.core.exceptions import ValidationError
from django.conf import settings
from sensor.models import Sensor
from decimal import Decimal

class Administrador(AbstractUser):
    rut = models.CharField(max_length=12, blank=True, null=True, unique=True, db_column='rut')
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.rut})"
    

def validate_delivery_date(value):
    if value < date.today():
        raise ValidationError("La fecha de entrega no puede ser anterior a hoy.")
   
    
class Cotizacion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    TIPO_SERVICIO = [
        ('', 'Seleccionar servicio...'),
        ('Granallado Ecológico PUING 13H₂O', 'Granallado Ecológico PUING 13H₂O'),
        ('Limpieza y Recuperación de Fachadas', 'Limpieza y Recuperación de Fachadas'),
        ('Procesos Metales y Preparación', 'Procesos Metales y Preparación'),
        ('Descontaminación Post-Incendio', 'Descontaminación Post-Incendio'),
        ('Eliminación de Rebabas y Preparación', 'Eliminación de Rebabas y Preparación'),
    ]
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )

    nombre = models.CharField(max_length=120)
    correo = models.EmailField(verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    empresa = models.CharField(max_length=100, blank=True, null=True)
    servicio = models.CharField(max_length=150, choices=TIPO_SERVICIO, default='')
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='cotizaciones_archivos/', blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)
    fecha_entrega = models.DateField(null=True,blank=True)

    def __str__(self):
        empresa = f" | {self.empresa}" if self.empresa else ""
        return f"Cotización - {self.nombre} {empresa} ({self.estado})"



class Herramienta(models.Model):
    ESTADOS = [
            ("disponible", "Disponible"),
            ("en_uso", "En uso"),
            ("en_reposo", "En reposo"),
        ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    sensor = models.ForeignKey(Sensor, null=True, blank=True, on_delete=models.SET_NULL)
    uid = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="disponible")
    def __str__(self):
        return f"[{self.nombre}] - [{self.sensor}]"

class Alerta(models.Model):
    TIPOS = [
        ("temperatura", "Temperatura Alta"),
        ("vibracion", "Vibración Elevada"),
        ("corriente", "Sobrecorriente"),
        ("horario", "Uso Fuera de Horario"),

    ]
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPOS)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    temperatura = models.FloatField(null=True, blank=True)
    vibracion = models.FloatField(null=True, blank=True)
    corriente = models.FloatField(null=True, blank=True)
    visto = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.tipo}] {self.herramienta.nombre} - {self.fecha:%Y-%m-%d %H:%M}"


class HistorialRFID(models.Model):
    ACCIONES = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
    ]
    herramienta = models.ForeignKey(Herramienta,on_delete=models.CASCADE,related_name="historial_rfid")
    sensor = models.ForeignKey(Sensor,on_delete=models.SET_NULL, null=True, blank=True, related_name="historial_rfid")
    uid = models.CharField(max_length=50)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)
    def _str_(self):
        sensor_info = f"Sensor {self.sensor.id}" if self.sensor else "Sin sensor"
        return f"{self.herramienta.nombre} - {self.accion} - {sensor_info} - {self.fecha:%d/%m/%Y %H:%M}"

class RegistroUsoHerramienta(models.Model):
    herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE)
    orden_trabajo = models.ForeignKey('Sistema_proyecto.OrdenTrabajo', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    energia_consumida = models.FloatField(default=0) 

    def __str__(self):
        return f"{self.herramienta.nombre} en OT #{self.orden_trabajo.id}"

class Presupuesto(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aceptado", "Aceptado"),
        ("rechazado", "Rechazado"),
    ]
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.CharField(max_length=200)
    servicio = models.CharField(max_length=255, blank=True, null=True)
    descripcion = models.TextField()
    monto_base = models.IntegerField(default=0, null=True, blank=True)
    monto_estimado = models.DecimalField(max_digits=12, decimal_places=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    archivo = models.FileField(upload_to='presupuestos_archivos/', null=True, blank=True)
    costo_energia = models.FloatField(default=0)
    energia_total = models.FloatField(default=0)
    herramienta = models.ForeignKey(Herramienta,null=True,blank=True,on_delete=models.SET_NULL)


    def __str__(self):
        return f"Presupuesto {self.id} - {self.cliente}"


class OrdenCompra(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, null=True, blank=True)
    numero_orden_compra = models.CharField(max_length=50, unique=True, editable=False, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE) 
    cliente = models.CharField(max_length=150)
    empresa = models.CharField(max_length=200)
    monto_total = models.DecimalField(max_digits=12, decimal_places=0)
    archivo = models.FileField(upload_to='ordenes_compra_archivos/', null=True, blank=True)


    def __str__(self):
        return f"OC {self.numero_orden_compra}"
    
class OrdenTrabajo(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('asignada', 'Asignada'),
        ('en_proceso', 'En proceso'),
        ('finalizada', 'Finalizada'),
        ('entregada', 'Entregada'),
    ]
    presupuesto = models.ForeignKey('Presupuesto',on_delete=models.CASCADE,null=True,blank=True)
    numero_ot = models.CharField(max_length=50, blank=True, null=True)
    cliente = models.CharField(max_length=200)  
    tecnico = models.ForeignKey('Trabajador', on_delete=models.SET_NULL, null=True, blank=True)  
    servicio = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_termino = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    herramientas = models.ManyToManyField('Herramienta', blank=True)
    energia_total_kwh = models.FloatField(default=0)
    costo_energia = models.DecimalField( max_digits=12,decimal_places=2,default=0)
    temp_promedio = models.FloatField(default=0)
    humedad_promedio = models.FloatField(default=0)
    vibracion_max = models.FloatField(default=0)
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.SET_NULL, null=True, blank=True)
    archivo = models.FileField(upload_to='ordenes_trabajo_archivos/', null=True, blank=True)



    def __str__(self):
        return f"OT #{self.id} - {self.servicio}"





class Factura(models.Model):
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, null=True, blank=True)
    orden_trabajo = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, null=True, blank=True)
    monto_neto = models.DecimalField(max_digits=14, decimal_places=2)
    costo_energia = models.DecimalField(max_digits=14, decimal_places=2)
    iva = models.DecimalField(max_digits=14, decimal_places=2)
    monto_total = models.DecimalField(max_digits=14, decimal_places=2)

    archivo_cotizacion = models.FileField(upload_to="facturas/cotizacion/", null=True, blank=True)
    archivo_presupuesto = models.FileField(upload_to="facturas/presupuesto/", null=True, blank=True)
    archivo_oc = models.FileField(upload_to="facturas/oc/", null=True, blank=True)
    archivo_ot = models.FileField(upload_to="facturas/ot/", null=True, blank=True)


    def __str__(self):
        return f"Factura {self.numero_factura}"
    
    def calcular_totales(self):
        subtotal = (self.monto_neto or 0) + (self.costo_energia or 0)
        self.iva = round(subtotal * Decimal("0.19"), 2)
        self.monto_total = round(subtotal + self.iva, 2)

    def save(self, *args, **kwargs):
        self.calcular_totales()
        super().save(*args, **kwargs)


class CondicionTaller(models.Model):
    temperatura = models.FloatField()
    humedad = models.FloatField()
    vibracion = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
    alerta = models.BooleanField(default=False)
    tipo_alerta = models.CharField(max_length=50, null=True, blank=True)
    detalle_alerta = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Condición del Taller {self.fecha}"

class ReporteGenerado(models.Model):
    tipo = models.CharField(max_length=100)  
    fecha = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='reportes/', null=True, blank=True)

    def __str__(self):
        return f"Reporte {self.tipo} - {self.fecha}"

class ComentarioOT(models.Model):
    autor= models.ForeignKey(Administrador, on_delete=models.CASCADE)
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    texto = models.TextField()

    def __str__(self):
        return f"Comentario OT {self.orden.id}"
    

class Trabajador(models.Model):
    nombre = models.CharField(max_length=120)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True, null=True)
    herramientas = models.ManyToManyField('Herramienta', blank=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
