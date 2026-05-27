#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from mediciones.models import Medicion
from sensor.models import Sensor

User = get_user_model()

class TestExportaciones(TestCase):
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
            descripcion="sensor fake"
        )
        Medicion.objects.create(
                sensor=self.sensor,
                voltaje=220,
                corriente=10,
                potencia=2200
            )
    def test_exportar_mediciones_excel(self):
        url = reverse("exportar_mediciones_excel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            response.headers["Content-Type"]
        )

    def test_exportar_informe_excel(self):
        url = reverse("exportar_informe_excel")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            response.headers["Content-Type"]
        )

    def test_limpiar_mediciones(self):
        self.assertEqual(Medicion.objects.count(), 1)

        url = reverse("limpiar_mediciones")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Medicion.objects.count(), 0)

    def test_respaldar_y_limpiar(self):
    # Forzar medición antigua
        m = Medicion.objects.first()
        m.fecha = timezone.now() - timezone.timedelta(days=10)
        m.save()

        url = reverse("respaldar_y_limpiar")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            response.headers["Content-Type"]
        )
