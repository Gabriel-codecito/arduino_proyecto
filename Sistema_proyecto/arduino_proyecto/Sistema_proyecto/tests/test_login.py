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


class TestLogin(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True
        )

        self.user = User.objects.create_user(
            username="cliente",
            password="1234",
            is_staff=False
        )

    def test_login_correcto_admin(self):
        resp = self.client.post(reverse("login"), {
            "username": "admin",
            "password": "1234"
        })
        self.assertEqual(resp.status_code, 302)

    def test_login_incorrecto(self):
        resp = self.client.post(reverse("login"), {
            "username": "admin",
            "password": "wrong"
        })
        self.assertEqual(resp.status_code, 302)

    def test_login_usuario_normal(self):
        resp = self.client.post(reverse("login"), {
            "username": "cliente",
            "password": "1234"
        })
        self.assertEqual(resp.status_code, 302)

    def test_logout(self):
        self.client.login(username="admin", password="1234")
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)

    def test_acceso_sin_login_redirige(self):
        resp = self.client.get(reverse("home_admin"))
        self.assertEqual(resp.status_code, 302)
