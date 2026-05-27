#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.core import mail
from django.urls import reverse
from mediciones.models import Medicion
from sensor.models import Sensor
from Sistema_proyecto.models import Herramienta
from Sistema_proyecto.utils import (
    validar_rut,
    staff_required,
    admin_required_redirect,
    enviar_notificacion_cotizacion,
    enviar_presupuesto_email,
    calcular_costo_energia
)

from Sistema_proyecto.models import Cotizacion, Presupuesto

User = get_user_model()


class TestUtils(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.admin = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True
        )

        self.usuario_normal = User.objects.create_user(
            username="normal",
            password="1234",
            is_staff=False
        )

        self.cot = Cotizacion.objects.create(
            nombre="Cliente Test",
            correo="cliente@test.com",
            servicio="Pintura",
            descripcion="Desc test",
            fecha_entrega="2030-01-01"
        )

        self.pres = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente Test",
            servicio="Pintura",
            descripcion="Texto",
            monto_estimado=50000
        )

    # ---------------------------------------------------------
    # 1) validar_rut
    # ---------------------------------------------------------
    def test_validar_rut_correcto(self):
        self.assertTrue(validar_rut("12345678", "5"))

    def test_validar_rut_incorrecto(self):
        self.assertFalse(validar_rut("12ABC678", "5"))
        self.assertFalse(validar_rut("", "K"))
        self.assertFalse(validar_rut("1234", "1"))

    # ---------------------------------------------------------
    # 2) staff_required
    # ---------------------------------------------------------
    def test_staff_required_usuario_no_autenticado(self):
        request = self.factory.get("/")
        request.user = type("obj", (), {"is_authenticated": False})()

        @staff_required
        def vista_test(request):
            return "ok"

        response = vista_test(request)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn(b"se requiere staff", response.content)

    def test_staff_required_usuario_no_staff(self):
        request = self.factory.get("/")
        request.user = self.usuario_normal

        @staff_required
        def vista_test(request):
            return "ok"

        response = vista_test(request)
        self.assertIsInstance(response, HttpResponseForbidden)
        self.assertIn(b"se requiere staff", response.content)

    def test_staff_required_usuario_staff(self):
        request = self.factory.get("/")
        request.user = self.admin

        @staff_required
        def vista_test(request):
            return "ok"

        self.assertEqual(vista_test(request), "ok")

    # ---------------------------------------------------------
    # 3) admin_required_redirect
    # ---------------------------------------------------------
    def test_admin_required_redirect_no_autenticado(self):
        request = self.factory.get("/")
        request.user = type("obj", (), {"is_authenticated": False})()

        @admin_required_redirect
        def vista_test(request):
            return "ok"

        resp = vista_test(request)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.url)

    def test_admin_required_redirect_no_staff(self):
        request = self.factory.get("/")
        request.user = self.usuario_normal

        @admin_required_redirect
        def vista_test(request):
            return "ok"

        resp = vista_test(request)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login", resp.url)

    def test_admin_required_redirect_staff(self):
        request = self.factory.get("/")
        request.user = self.admin

        @admin_required_redirect
        def vista_test(request):
            return "ok"

        self.assertEqual(vista_test(request), "ok")

    # ---------------------------------------------------------
    # 4) enviar_notificacion_cotizacion
    # ---------------------------------------------------------
    def test_enviar_notificacion_cotizacion_envia_correo(self):
        enviar_notificacion_cotizacion(self.cot, "aprobada")

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Actualización de tu cotización", mail.outbox[0].subject)
        self.assertIn("aprobada", mail.outbox[0].body.lower())

    # ---------------------------------------------------------
    # 5) enviar_presupuesto_email
    # ---------------------------------------------------------
    def test_enviar_presupuesto_email_envia_correo(self):
        enviar_presupuesto_email(self.pres)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Presupuesto", mail.outbox[0].subject)
        self.assertIn("aceptar", mail.outbox[0].body.lower())


    def test_calcular_costo_energia(self):
        sensor = Sensor.objects.create(nombre="Sensor Test")

        herramienta = Herramienta.objects.create(
            nombre="Taladro Test",
            estado="disponible"
        )

        Medicion.objects.create(
            sensor=sensor,
            herramienta=herramienta,
            voltaje=220,
            corriente=5,          # genera potencia real
            factor_potencia=1
        )

        Medicion.objects.create(
            sensor=sensor,
            herramienta=herramienta,
            voltaje=220,
            corriente=5,
            factor_potencia=1
        )

        energia_total, costo = calcular_costo_energia(herramienta, tarifa_kw=100)

        self.assertGreater(energia_total, 0)
        self.assertGreater(costo, 0)
