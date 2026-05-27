#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from django.test import TestCase, Client
from Sistema_proyecto.models import (
    Factura, OrdenTrabajo, Presupuesto,
    Cotizacion, OrdenCompra
)
from django.contrib.auth import get_user_model
from datetime import date
from django.urls import reverse
from decimal import Decimal

User = get_user_model()


class TestFacturaViews(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        self.client.login(username="admin", password="admin123")

        self.cot = Cotizacion.objects.create(
            nombre="X",
            correo="x@test.com",
            servicio="S",
            empresa="Empresa X",
            descripcion="D",
            fecha_entrega=date.today()
        )

        self.presu = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Juan",
            servicio="Servicio X",
            descripcion="algo",
            monto_estimado=Decimal("10000")
        )

        self.ot = OrdenTrabajo.objects.create(
            cliente="Juan",
            servicio="Servicio X",
            descripcion="Desc",
            presupuesto=self.presu,
            estado="entregada"
        )

        self.oc = OrdenCompra.objects.create(
            cotizacion=self.cot,
            presupuesto=self.presu,
            cliente="Juan",
            empresa="Empresa X",
            monto_total=Decimal("10000")
        )
    def test_facturar_ot(self):
        url = reverse("facturar_ot", args=[self.ot.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


    def test_factura_str(self):
        factura = Factura.objects.create(
            numero_factura="F001",
            orden_compra=self.oc,
            orden_trabajo=self.ot,
            monto_neto=Decimal("500"),
            costo_energia=Decimal("0"),
            iva=Decimal("95"),
            monto_total=Decimal("595")
        )

        self.assertEqual(str(factura), "Factura F001")
