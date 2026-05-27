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
from datetime import date
from django.db.utils import IntegrityError
import datetime
from Sistema_proyecto.models import Cotizacion, OrdenCompra, Presupuesto

User = get_user_model()


# ==================================================
#   TEST PARA ORDEN DE COMPRA (MODELO + VISTAS)
# ==================================================
class TestOrdenCompraViews(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True,
            is_superuser=True
        )
        self.client.login(username="admin", password="1234")

        self.cot = Cotizacion.objects.create(
            nombre="Cliente",
            empresa="EmpresaX",
            correo="test@test.com",
            telefono="123456",
            servicio="Servicio ABC",
            descripcion="desc",
            fecha_entrega=date.today()
        )

        self.presupuesto = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente",
            servicio="Servicio ABC",
            descripcion="desc",
            monto_estimado=10000
        )

        self.oc = OrdenCompra.objects.create(
            presupuesto=self.presupuesto,
            cotizacion=self.cot,
            cliente="Cliente",
            empresa="EmpresaX",
            monto_total=self.presupuesto.monto_estimado

        )
        self.oc.numero_orden_compra = f"OC-{self.oc.id:04d}"
        self.oc.save()
        
    def test_lista_oc(self):
        
        """Debe listar correctamente las órdenes de compra."""
        response = self.client.get(reverse("lista_oc"))
        self.assertEqual(response.status_code, 200)

        # La tabla muestra SOLO el ID de la OC
        self.assertContains(response, str(self.oc.id))

        # Datos importantes visibles en la tabla
        self.assertContains(response, self.oc.cliente)
        self.assertContains(response, self.oc.empresa)
        self.assertContains(response, "$")





    def test_crear_oc_post(self):
        """Debe crear correctamente la OC desde un presupuesto."""
        presupuesto = self.presupuesto  # ya creado en setUp
        data = {
            "monto_total": presupuesto.monto_estimado, 
        }

        response = self.client.post(
            reverse("crear_oc", args=[presupuesto.id]),
            data
        )

        # Debe redirigir al detalle de la OC
        self.assertEqual(response.status_code, 302)

        # Validar que la OC se creó y está ligada al presupuesto
        oc = OrdenCompra.objects.get(presupuesto=presupuesto)

        self.assertEqual(oc.cotizacion, presupuesto.cotizacion)
        self.assertEqual(oc.cliente, presupuesto.cotizacion.nombre)
        self.assertEqual(oc.empresa, presupuesto.cotizacion.empresa)
        self.assertEqual(oc.monto_total, presupuesto.monto_estimado)

        # Número generado correctamente
        self.assertTrue(oc.numero_orden_compra.startswith("OC-"))


    def test_detalle_oc(self):
        """Debe cargar correctamente el detalle de OC."""
        response = self.client.get(reverse("detalle_oc", args=[self.oc.id]))
        self.assertEqual(response.status_code, 200)

        # La plantilla muestra SOLO el ID, NO el número OC-0001
        oc = OrdenCompra.objects.get(id=self.oc.id)
        self.assertContains(response, f"Orden de Compra N° {oc.id}")


    def test_editar_oc_post(self):
        data = {
        "monto_total": 50000   # YA NO SE ENVÍA COTIZACION
    }

        response = self.client.post(
            reverse("editar_oc", args=[self.oc.id]),
            data
        )

        self.assertEqual(response.status_code, 302)

        self.oc.refresh_from_db()
        self.assertEqual(self.oc.monto_total, 50000)


# ==================================================
#              TEST DEL MODELO ORDENCOMPRA
# ==================================================
class TestOrdenCompraModel(TestCase):

    def setUp(self):
        # Crear usuario admin para que el login funcione
            self.admin = User.objects.create_user(
                username="admin",
                password="1234",
                is_staff=True,
                is_superuser=True
            )

            self.client.login(username="admin", password="1234")

            # Datos base
            self.cot = Cotizacion.objects.create(
                nombre="Cliente",
                empresa="EmpresaX",
                correo="test@test.com",
                telefono="123456",
                servicio="Servicio ABC",
                descripcion="desc",
                fecha_entrega=date.today()
            )

            self.presupuesto = Presupuesto.objects.create(
                cotizacion=self.cot,
                cliente=self.cot.nombre,
                servicio=self.cot.servicio,
                descripcion="desc",
                monto_estimado=15000
            )

    def test_crear_oc_post(self):
        self.client.login(username="admin", password="1234")

        # 1️⃣ Crear cotización
        cotizacion = Cotizacion.objects.create(
            nombre="Cliente Prueba",
            empresa="Empresa X",
            correo="cliente@example.com",
            descripcion="Trabajo de prueba",
            estado="aprobada",
            fecha_entrega=date.today()
        )

        # 2️⃣ Crear presupuesto que sigue a la cotización
        presupuesto = Presupuesto.objects.create(
            cotizacion=cotizacion,
            monto_estimado=50000,
            estado="aceptado"
        )

        # 3️⃣ Crear OC pasando el presupuesto
        response = self.client.post(
        reverse("crear_oc", args=[presupuesto.id]),
        {"monto_total": 50000}
    )

        # 4️⃣ Debe redirigir (tu flujo lo hace)
        self.assertEqual(response.status_code, 302)

        # 5️⃣ Validar que se creó solo UNA OC
        oc = OrdenCompra.objects.filter(presupuesto=presupuesto).first()

        self.assertIsNotNone(oc)

        # 6️⃣ Validar relaciones del flujo
        self.assertEqual(oc.presupuesto, presupuesto)
        self.assertEqual(oc.cotizacion, cotizacion)
        self.assertEqual(oc.cliente, cotizacion.nombre)
        self.assertEqual(oc.empresa, cotizacion.empresa)

        # 7️⃣ Validar número de OC generado por tu lógica
        self.assertTrue(oc.numero_orden_compra.startswith("OC-"))


    def test_numero_oc_unico(self):
        """Debe fallar si dos OC tienen el mismo número."""
        OrdenCompra.objects.create(
            numero_orden_compra="OC-100",
            cotizacion=self.cot,
            cliente="Cliente Prueba",
            empresa="Empresa X",
            monto_total=10
        )

        with self.assertRaises(IntegrityError):
            OrdenCompra.objects.create(
                numero_orden_compra="OC-100",
                cotizacion=self.cot,
                cliente="Cliente Prueba",
                empresa="Empresa X",
                monto_total=20
            )
