#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
from Sistema_proyecto.models import (Presupuesto, Factura, OrdenCompra,Cotizacion, OrdenTrabajo)
from decimal import Decimal

User = get_user_model()


# =============================
#     PRESUPUESTO VIEWS
# =============================
class TestPresupuestoViews(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="123", is_staff=True
        )
        self.client.login(username="admin", password="123")

        self.cot = Cotizacion.objects.create(
            nombre="Cliente",
            empresa="EmpresaX",
            correo="test@test.com",
            telefono="1234",
            servicio="X",
            descripcion="desc",
            fecha_entrega=date.today()
        )


        self.presupuesto = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente 1",
            servicio="Servicio 1",
            descripcion="Desc",
            monto_estimado=1000
        )

    def test_lista_presupuestos(self):
        response = self.client.get(reverse("lista_presupuestos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente 1")


# =============================
#     ORDEN DE COMPRA VIEWS
# =============================
class TestOrdenCompraViews(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="12345", is_staff=True
        )
        self.client.login(username="admin", password="12345")

        # Cotización base
        self.cot = Cotizacion.objects.create(
            nombre="Cliente",
            empresa="EmpresaX",
            correo="test@test.com",
            telefono="1234",
            servicio="X",
            descripcion="desc",
            fecha_entrega=date.today()
        )


        # Presupuesto base (OBLIGATORIO para flujo)
        self.presu = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente=self.cot.nombre,
            servicio=self.cot.servicio,
            descripcion="desc",
            monto_estimado=1000
        )

        # Orden de compra válida
        self.oc = OrdenCompra.objects.create(
            numero_orden_compra="OC-10",
            presupuesto=self.presu,
            cotizacion=self.cot,
            empresa="P&U",
            cliente=self.cot.nombre,
            monto_total=1000
        )

    def test_lista_oc(self):
        response = self.client.get(reverse("lista_oc"))
        self.assertEqual(response.status_code, 200)

        # Se muestra el ID, no el número OC-0001
        self.assertContains(response, "$")




    def test_crear_oc_post(self):
        self.client.login(username="admin", password="12345")

        cotizacion = Cotizacion.objects.create(
            nombre="Cliente Prueba",
            empresa="Empresa X",
            correo="cliente@example.com",
            descripcion="Trabajo de prueba",
            estado="aprobada",
            fecha_entrega=date.today()
        )

        presupuesto = Presupuesto.objects.create(
            cotizacion=cotizacion,
            monto_estimado=50000,
            estado="aceptado"
        )

        response = self.client.post(
            reverse("crear_oc", args=[presupuesto.id]),
            {"monto_total": 50000}
        )

        self.assertEqual(response.status_code, 302)

        oc = OrdenCompra.objects.last()
        self.assertIsNotNone(oc)

        self.assertEqual(oc.presupuesto, presupuesto)
        self.assertEqual(oc.cotizacion, cotizacion)
        self.assertEqual(oc.cliente, cotizacion.nombre)
        self.assertEqual(oc.empresa, cotizacion.empresa)

        self.assertTrue(oc.numero_orden_compra.startswith("OC-"))

    def test_detalle_oc(self):
        response = self.client.get(reverse("detalle_oc", args=[self.oc.id]))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, f"Orden de Compra N° {self.oc.id}")


    def test_editar_oc_post(self):
        response = self.client.post(
            reverse("editar_oc", args=[self.oc.id]),
            {"monto_total": 50000}
        )

        self.assertEqual(response.status_code, 302)

        self.oc.refresh_from_db()
        self.assertEqual(self.oc.monto_total, 50000)


# =============================
#     FACTURA VIEWS
# =============================
class TestFacturaCRUD(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="123", is_staff=True)
        self.client.login(username="admin", password="123")
        


        # Crear cotización
        self.cot = Cotizacion.objects.create(
                nombre="Cliente",
                empresa="EmpresaX",
                correo="test@test.com",
                telefono="1234",
                servicio="X",
                descripcion="desc",
                fecha_entrega=date.today(),
                archivo=SimpleUploadedFile("cotizacion_test.pdf",
            b"%PDF-1.4\n% Esto es un PDF falso pero con mas contenido\n1 0 obj\n<< /Type /Catalog >>\nendobj"
        )
                )
                
        

        # Crear presupuesto asociado
        self.pres = Presupuesto.objects.create(
            cotizacion=self.cot,
            monto_estimado=10000,
            estado="aceptado"
        )

        # Crear OC porque la vista facturar necesita una
        self.oc = OrdenCompra.objects.create(
            presupuesto=self.pres,
            cotizacion=self.cot,
            cliente=self.cot.nombre,
            empresa=self.cot.empresa,
            monto_total=10000,
            numero_orden_compra="OC-0001"
        )

        # Crear OT asociada a la OC
        self.ot = OrdenTrabajo.objects.create(
            presupuesto=self.pres,
            orden_compra=self.oc
        )
        
        self.factura = Factura.objects.create(
            numero_factura="F-555",
            orden_trabajo=self.ot,
            orden_compra=self.oc,
            monto_neto=Decimal("10000"),
            costo_energia=Decimal("0"),
            iva=Decimal("1900"),
            monto_total=Decimal("11900")
        )

    def test_lista_facturas(self):
        response = self.client.get(reverse("lista_facturas"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "F-555")

    def test_facturar_ot_post(self):
        response = self.client.get(reverse("facturar_ot", args=[self.ot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Factura.objects.count(), 1)

    def test_detalle_factura(self):
        response = self.client.get(reverse("detalle_factura", args=[self.factura.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "F-555")

    
