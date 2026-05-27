#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.test import TestCase
from django.db.utils import IntegrityError
from django.urls import reverse
from Sistema_proyecto.models import Presupuesto, OrdenCompra, Factura, Cotizacion
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import datetime
User = get_user_model()
from decimal import Decimal

# =============================
#        PRESUPUESTO
# =============================
class TestPresupuestoModel(TestCase):

    def setUp(self):
        self.cot = Cotizacion.objects.create(
            nombre="Empresa X",
            correo="cliente@test.com",
            servicio="Servicio A",
            empresa="Empresa X",        # ← NECESARIA
            descripcion="desc",
            fecha_entrega=date.today(),
            estado="aprobada"
        )

    def test_creacion_presupuesto(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente=self.cot.nombre,
            servicio="Mantenimiento",
            descripcion="Presupuesto general",
            monto_estimado=150000
        )

        self.assertEqual(p.cliente, self.cot.nombre)
        self.assertEqual(p.monto_estimado, 150000)
        self.assertIn("Presupuesto", str(p))

    def test_monto_negativo(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente=self.cot.nombre,
            servicio="Servicio",
            descripcion="Desc",
            monto_estimado=-100
        )
        self.assertLess(p.monto_estimado, 0)

    def test_presupuesto_estado_default(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente=self.cot.nombre,
            servicio="Servicio Z",
            descripcion="Desc",
            monto_estimado=15000
        )
        self.assertEqual(p.estado, "pendiente")

    def test_presupuesto_str(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente ABC",
            servicio="Servicio 1",
            descripcion="Test",
            monto_estimado=999
        )
        self.assertEqual(str(p), f"Presupuesto {p.id} - Cliente ABC")



# =============================
#     ORDEN DE COMPRA
# =============================
class TestOrdenCompraModel(TestCase):

    def setUp(self):
        self.cot = Cotizacion.objects.create(
            nombre="Cliente Juan",
            empresa="Empresa Juan SA",      # ← NECESARIA
            correo="juan@test.com",
            servicio="Servicio",
            descripcion="Test OC",
            fecha_entrega=date.today(),
            estado="aprobada",
            
        )

        self.user = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True
        )

    def test_crear_oc_post(self):
        self.client.login(username="admin", password="1234")

        cot = Cotizacion.objects.create(
            nombre="Cliente Prueba",
            empresa="EmpresaX",
            correo="cliente@test.com",
            telefono="987654",
            servicio="Servicio X",
            descripcion="desc",
            fecha_entrega=date.today()
        )

        presupuesto = Presupuesto.objects.create(
            cotizacion=cot,
            cliente=cot.nombre,
            servicio=cot.servicio,
            descripcion="Desc",
            monto_estimado=10000
        )

        url = f"/oc/crear/{presupuesto.id}/"
        data = {
            "empresa": presupuesto.cotizacion.empresa if presupuesto.cotizacion else "Empresa",
            "cliente": presupuesto.cliente,
            "monto_total": presupuesto.monto_estimado,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(OrdenCompra.objects.count(), 1)

        oc = OrdenCompra.objects.first()
        self.assertEqual(oc.presupuesto.id, presupuesto.id)


    def test_numero_oc_unico(self):
        OrdenCompra.objects.create(
            numero_orden_compra="OC-100",
            cotizacion=self.cot,
            empresa=self.cot.empresa,
            cliente=self.cot.nombre,
            monto_total=10
        )

        with self.assertRaises(IntegrityError):
            OrdenCompra.objects.create(
                numero_orden_compra="OC-100",
                cotizacion=self.cot,
                empresa=self.cot.empresa,
                cliente=self.cot.nombre,
                monto_total=20
            )



# =============================
#           FACTURA
# =============================
class TestFacturaModel(TestCase):

    def setUp(self):

        self.cot = Cotizacion.objects.create(
            nombre="Cliente Y",
            empresa="Empresa Y Spa",      # ← NECESARIA
            correo="y@test.com",
            servicio="Servicio",
            descripcion="Test Factura",
            fecha_entrega=date.today(),
            estado="aprobada",
        )

        self.oc = OrdenCompra.objects.create(
            numero_orden_compra="OC-002",
            cotizacion=self.cot,
            cliente=self.cot.nombre,
            empresa=self.cot.empresa,
            monto_total=300000
        )

    def test_facturar_ot(self):
        f = Factura.objects.create(
        numero_factura="F-2024-001",
        orden_compra=self.oc,
        monto_neto=Decimal("300000"),
        costo_energia=Decimal("0"),
        iva=Decimal("57000"),
        monto_total=Decimal("357000")
    )

        self.assertEqual(str(f), "Factura F-2024-001")

    def test_numero_factura_unico(self):
        Factura.objects.create(
            numero_factura="F-500",
            orden_compra=self.oc,
            monto_neto=1000,
            costo_energia=0,
            iva=190,
            monto_total=1190
        )


        with self.assertRaises(IntegrityError):
            Factura.objects.create(
                numero_factura="F-500",
                orden_compra=self.oc,
                monto_neto=2000
            )
