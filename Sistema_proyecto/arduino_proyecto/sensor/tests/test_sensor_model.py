#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.test import TestCase
from sensor.models import Sensor
from Sistema_proyecto.models import Administrador as User


class TestSensorModel(TestCase):

    def test_str(self):
        s = Sensor.objects.create(nombre="S1")
        self.assertEqual(str(s), "S1")

    def test_valores_por_defecto(self):
        s = Sensor.objects.create(nombre="S2")
        self.assertEqual(s.tipo, "SCT-013")
        self.assertEqual(s.estado, "inactivo")
        self.assertEqual(s.ubicacion_fija, "Taller Principal")