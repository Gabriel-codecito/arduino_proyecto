#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from mediciones.models import Medicion
from Sistema_proyecto.models import Cotizacion, Administrador
from sensor.models import Sensor


User = get_user_model()
class TestAdministrador(TestCase):

    def test_creacion_admin(self):
        admin = Administrador.objects.create_user(
            username="jefa",
            password="12345",
            rut="12.345.678-9",
            telefono="987654321",
            is_staff=True
        )

        self.assertEqual(admin.username, "jefa")
        self.assertEqual(admin.rut, "12.345.678-9")
        self.assertTrue(admin.check_password("12345"))
        self.assertTrue(admin.is_staff)

class TestDashboardAdmin(TestCase):

    def setUp(self):
        # Usuario staff
        self.admin = User.objects.create_user(
            username="admin",
            password="123",
            is_staff=True
        )

        # Datos fake
        self.sensor = Sensor.objects.create(nombre="Sensor X")
        Medicion.objects.create(
            sensor=self.sensor,
            corriente=0.5,
            energia=1.2,
            fecha=timezone.now()
        )
        Cotizacion.objects.create(
            nombre="Juan",
            correo="a@b.com",
            telefono="111",
            empresa="Test",
            servicio="Servicio X",
            descripcion="Test",
            fecha_entrega="2099-01-01"
        )

    def test_dashboard_restringido_no_staff(self):
        user = User.objects.create_user("cliente", password="123", is_staff=False)
        self.client.login(username="cliente", password="123")

        response = self.client.get(reverse("home_admin"))

        # Como está login_required, redirige
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_dashboard_staff_ok(self):
        self.client.login(username="admin", password="123")

        response = self.client.get(reverse("home_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sensores Activos")
        self.assertTemplateUsed(response, "Sistema_proyecto/administrador/home_admin.html")
