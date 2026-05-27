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
from django.contrib.messages import get_messages

User = get_user_model()


class TestAuthViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.url_login = reverse("login")
        self.url_logout = reverse("logout")
        self.url_registro = reverse("registro")
        self.url_home_admin = reverse("home_admin")

    # ---------------------------------------------------------
    # 1) LOGIN
    # ---------------------------------------------------------

    def test_login_get_carga_template(self):
        """Debe cargar correctamente el template de login en GET."""
        response = self.client.get(self.url_login)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Sistema_proyecto/login.html")

    def test_login_post_correcto(self):
        """Debe autenticar y redirigir al panel admin."""
        User.objects.create_user(
            username="admin", password="1234", is_staff=True
        )

        response = self.client.post(self.url_login, {
            "username": "admin",
            "password": "1234"
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_home_admin)

    def test_login_post_incorrecto(self):
        """Si las credenciales son inválidas debe redirigir al login."""
        response = self.client.post(self.url_login, {
            "username": "nadie",
            "password": "mal"
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_login)

        # Validar mensaje
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("incorrectos" in m.message.lower() for m in mensajes))

    # ---------------------------------------------------------
    # 2) LOGOUT
    # ---------------------------------------------------------

    def test_logout_cierra_sesion(self):
        user = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True
        )

        self.client.login(username="admin", password="1234")

        response = self.client.get(self.url_logout)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_login)

        # Verificar mensaje
        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("cerrada" in m.message.lower() for m in mensajes))

    # ---------------------------------------------------------
    # 3) REGISTRO DE ADMIN
    # ---------------------------------------------------------

    def test_registro_crea_una_unica_admin(self):
        """Debe permitir crear solo una administradora."""
        response = self.client.post(self.url_registro, {
            "rut": "12345678",
            "dv": "5",
            "username": "admin1",
            "telefono": "999999",
            "password": "1234",
            "password2": "1234",
        })

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_login)

    def test_registro_no_permite_segunda_admin(self):
        """Si ya existe una admin, debe bloquear el registro."""
        User.objects.create_user(
            username="admin1",
            password="1234",
            rut="12345678-5",
            is_staff=True
        )

        response = self.client.post(self.url_registro, {
            "rut": "87654321",
            "dv": "K",
            "username": "admin2",
            "telefono": "5555",
            "password": "abcd",
            "password2": "abcd",
        })

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url_login)

        mensajes = list(get_messages(response.wsgi_request))
        self.assertEqual(User.objects.count(), 2)


    def test_registro_contrasenas_no_coinciden(self):
        """Debe mostrar error si las contraseñas no coinciden."""
        response = self.client.post(self.url_registro, {
            "rut": "12345678",
            "dv": "5",
            "username": "adminX",
            "telefono": "12345",
            "password": "1111",
            "password2": "2222",
        })

        self.assertEqual(User.objects.count(), 0)
        self.assertRedirects(response, self.url_registro)

        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("no coinciden" in m.message.lower() for m in mensajes))

    def test_registro_rut_incompleto(self):
        """Debe mostrar error si falta rut o dv."""
        response = self.client.post(self.url_registro, {
            "rut": "",
            "dv": "",
            "username": "adminX",
            "telefono": "12345",
            "password": "1111",
            "password2": "1111",
        })

        self.assertEqual(User.objects.count(), 0)
        self.assertRedirects(response, self.url_registro)

        mensajes = list(get_messages(response.wsgi_request))
        self.assertTrue(any("debe ingresar el rut completo" in m.message.lower() for m in mensajes))
