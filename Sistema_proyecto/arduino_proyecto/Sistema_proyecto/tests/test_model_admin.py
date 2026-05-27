#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from Sistema_proyecto.models import (
    Cotizacion,
    Herramienta,
    OrdenTrabajo,
    Presupuesto,
    OrdenCompra,
    Factura,
    CondicionTaller,
    ComentarioOT
)

User = get_user_model()


# ---------------------------------------------------------
# 1) Administrador.__str__
# ---------------------------------------------------------
class TestAdministradorStr(TestCase):
    def test_admin_str(self):
        admin = User.objects.create_user(
            username="paula",
            password="123",
            rut="11.111.111-1"
        )
        self.assertEqual(str(admin), "paula (11.111.111-1)")


# ---------------------------------------------------------
# 2) validate_delivery_date
# ---------------------------------------------------------
class TestValidateDeliveryDate(TestCase):
    def test_fecha_anterior_error(self):
        cot = Cotizacion(
            nombre="Cliente",
            correo="c@c.cl",
            telefono="123",
            empresa="X",
            servicio="Test",
            descripcion="aaaa",
            fecha_entrega=date.today() - timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            cot.full_clean()

    def test_fecha_valida_ok(self):
        cot = Cotizacion(
            nombre="Cliente",
            correo="c@c.cl",
            telefono="123",
            empresa="X",
            servicio="Test",
            descripcion="aaaa",
            fecha_entrega=date.today() + timedelta(days=1)
        )
        cot.full_clean()  # No debe fallar


# ---------------------------------------------------------
# 3) Herramienta.__str__
# ---------------------------------------------------------
class TestHerramientaStr(TestCase):
    def test_herramienta_str(self):
        h = Herramienta.objects.create(
            nombre="Taladro",
            descripcion="",
            estado="disponible"
        )
        self.assertIn("Taladro", str(h))




# ---------------------------------------------------------
# 4) Presupuesto.__str__
# ---------------------------------------------------------
class TestPresupuestoStr(TestCase):
    def test_presupuesto_str(self):

        # Crear cotización requerida por el modelo
        cot = Cotizacion.objects.create(
            nombre="Empresa X",
            correo="c@test.com",
            telefono="123",
            empresa="X",
            servicio="Servicio A",
            descripcion="desc",
            fecha_entrega=date.today() + timedelta(days=1),
            estado="aprobada"
        )

        p = Presupuesto.objects.create(
            cotizacion=cot,
            cliente="Empresa X",
            servicio="Servicio A",
            descripcion="desc",
            monto_estimado=100
        )

        self.assertIn("Presupuesto", str(p))
        self.assertIn("Empresa X", str(p))


# ---------------------------------------------------------
# 5) Factura.__str__
# ---------------------------------------------------------
class TestFacturaStr(TestCase):
    def test_factura_str(self):

        cot = Cotizacion.objects.create(
            nombre="Cliente",
            correo="c@c.cl",
            telefono="123",
            empresa="X",
            servicio="Test",
            descripcion="aaaa",
            fecha_entrega=date.today() + timedelta(days=1),
            estado="aprobada"
        )

        oc = OrdenCompra.objects.create(
            numero_orden_compra="OC123",
            cotizacion=cot,
            empresa="Empresa",
            cliente="Cliente",
            monto_total=1000
        )

        f = Factura.objects.create(
            numero_factura="F001",
            orden_compra=oc,
            monto_neto=500,
            costo_energia=0,
            iva=95,
            monto_total=595)

        self.assertEqual(str(f), "Factura F001")


# ---------------------------------------------------------
# 6) CondicionTaller.__str__
# ---------------------------------------------------------
class TestCondicionTallerStr(TestCase):
    def test_condicion_str(self):
        c = CondicionTaller.objects.create(
            temperatura=25,
            humedad=50,
            vibracion=0.5
        )
        self.assertIn("Condición del Taller", str(c))
