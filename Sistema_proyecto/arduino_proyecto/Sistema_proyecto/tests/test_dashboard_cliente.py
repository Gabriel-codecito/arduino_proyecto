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

User = get_user_model()

class TestDashboardInformes(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username="admin_dash",
            password="1234",
            is_staff=True
        )
        self.client.login(username="admin_dash", password="1234")

    def test_reportes_admin_ok(self):
        response = self.client.get(reverse("reportes_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Sistema_proyecto/reportes/reportes_admin.html")

    def test_perfil_admin_ok(self):
        response = self.client.get(reverse("perfil_admin"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Sistema_proyecto/administrador/perfil_admin.html")
