#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from mediciones.models import Medicion
from sensor.models import Sensor

User = get_user_model()

class TestAlertasView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        self.client.login(username="admin", password="admin123")

        self.sensor = Sensor.objects.create(
            nombre="Sensor Test",
            tipo="corriente",
            descripcion="Sensor pruebas"
        )

    def test_alertas_lista(self):
        # Medición con valores críticos
        Medicion.objects.create(
            sensor=self.sensor,
            temperatura=45,   # genera alerta
            vibracion=60,     # genera alerta
            corriente=3       # genera alerta
        )

        url = reverse("alertas_lista")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Temperatura")
        self.assertContains(response, "Vibración")


class TestInformeEnergia(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        self.client.login(username="admin", password="admin123")

        self.sensor = Sensor.objects.create(
            nombre="Sensor Energía",
            tipo="corriente",
            descripcion="Sensor energía test"
        )

        Medicion.objects.create(
            sensor=self.sensor,
            voltaje=220,
            corriente=5
        )

    def test_informe_energia(self):
        url = reverse("informe_energia")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("datos", response.context)
        self.assertGreaterEqual(len(response.context["datos"]), 1)