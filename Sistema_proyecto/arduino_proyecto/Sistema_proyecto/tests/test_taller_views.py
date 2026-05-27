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
from Sistema_proyecto.models import CondicionTaller
from mediciones.models import Medicion
from django.utils import timezone
from sensor.models import Sensor
from datetime import timedelta
User = get_user_model()


class TestCondicionTallerViews(TestCase):

    def setUp(self):
        # 🔐 Usuario requerido por LoginRequiredMixin
        self.user = User.objects.create_user(
            username="admin",
            password="123",
            is_staff=True
        )
        self.client.login(username="admin", password="123")

        # 🔌 SENSOR (OBLIGATORIO para Medicion)
        self.sensor = Sensor.objects.create(
            nombre="Sensor Test",
            tipo="DHT22"
        )

    def test_lista_condiciones(self):
        Medicion.objects.create(
            sensor=self.sensor,
            temperatura=25,
            humedad=50,
            vibracion=10,
            fecha=timezone.now()
        )

        response = self.client.get("/taller/condiciones/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("registros", response.context)
        self.assertEqual(len(response.context["registros"]), 1)

    def test_lista_condiciones_ordenadas(self):
        Medicion.objects.create(
            sensor=self.sensor,
            temperatura=30,
            humedad=60,
            vibracion=20,
            fecha=timezone.now() - timedelta(minutes=10)
        )

        Medicion.objects.create(
            sensor=self.sensor,
            temperatura=20,
            humedad=40,
            vibracion=5,
            fecha=timezone.now()
        )

        response = self.client.get("/taller/condiciones/")
        registros = response.context["registros"]

        self.assertGreaterEqual(len(registros), 2)
        self.assertGreaterEqual(registros[0].fecha, registros[1].fecha)
