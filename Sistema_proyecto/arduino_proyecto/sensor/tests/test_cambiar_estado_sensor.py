#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from sensor.models import Sensor
from mediciones.models import Medicion
from sensor.views import cambiar_estado_sensor
from Sistema_proyecto.models import Administrador as User
from unittest.mock import MagicMock


class TestCambiarEstadoSensor(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.staff = User.objects.create_user(username="admin", password="123", is_staff=True)
        self.no_staff = User.objects.create_user(username="user", password="123", is_staff=False)
        self.sensor = Sensor.objects.create(nombre="S1")

    def test_cliente_no_puede_cambiar_estado(self):
        req = self.factory.get("/?estado=activo")
        req.user = self.no_staff

        resp = cambiar_estado_sensor(req, self.sensor.pk)

        self.assertEqual(resp.status_code, 403)
        self.assertIn("No tienes permiso", resp.content.decode())

    def test_staff_sin_mediciones_redirige(self):
        req = self.factory.get("/?estado=activo")
        req.user = MagicMock()
        req.user.is_authenticated = True
        req.user.is_staff = True



        resp = cambiar_estado_sensor(req, self.sensor.pk)

        self.assertEqual(resp.status_code, 302)
        self.assertIn("sensores", resp.url)

    def test_staff_con_mediciones_retorna_200(self):
        # Crear una medición para activar la rama del código
        Medicion.objects.create(sensor=self.sensor, corriente=1, energia=1)

        req = self.factory.get("/?estado=activo")
        req.user = MagicMock()
        req.user.is_authenticated = True
        req.user.is_staff = True



        resp = cambiar_estado_sensor(req, self.sensor.pk)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Estado actualizado correctamente", resp.content.decode())
