#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.urls import reverse
from django.test import TestCase
from sensor.models import Sensor
from mediciones.models import Medicion
from Sistema_proyecto.models import Administrador as User



class TestPaginaSensores(TestCase):

    def setUp(self):
        self.user_staff = User.objects.create_user(username="admin", password="123", is_staff=True)
        self.user_client = User.objects.create_user(username="cliente", password="123", is_staff=False)

    def test_pagina_sensores_redirige_no_logueado(self):
        resp = self.client.get(reverse("sensores"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.url)

    def test_pagina_sensores_forbidden_no_staff(self):
        self.client.login(username="cliente", password="123")
        resp = self.client.get(reverse("sensores"))
        self.assertEqual(resp.status_code, 302)

    def test_pagina_sensores_ok_staff(self):
        self.client.login(username="admin", password="123")
        resp = self.client.get(reverse("sensores"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "Sistema_proyecto/administrador/sensores.html")


class TestCambiarEstadoSensor(TestCase):

    def setUp(self):
        self.user_staff = User.objects.create_user(username="admin", password="123", is_staff=True)
        self.user_cliente = User.objects.create_user(username="cliente", password="123", is_staff=False)

        self.sensor = Sensor.objects.create(nombre="S1")

    def test_cambiar_estado_forbidden_no_staff(self):
        self.client.login(username="cliente", password="123")
        url = reverse("cambiar_estado_sensor", args=[self.sensor.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_cambiar_estado_con_medicion_devuelve_200(self):
        Medicion.objects.create(sensor=self.sensor, voltaje=1, corriente=1, potencia=1, energia=1)

        self.client.login(username="admin", password="123")
        url = reverse("cambiar_estado_sensor", args=[self.sensor.id])
        resp = self.client.get(url, {"estado": "activo"})

        self.assertEqual(resp.status_code, 200)
        self.sensor.refresh_from_db()
        self.assertEqual(self.sensor.estado, "activo")

    def test_cambiar_estado_sin_medicion_redirige(self):
        self.client.login(username="admin", password="123")
        url = reverse("cambiar_estado_sensor", args=[self.sensor.id])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("sensores", resp.url)
