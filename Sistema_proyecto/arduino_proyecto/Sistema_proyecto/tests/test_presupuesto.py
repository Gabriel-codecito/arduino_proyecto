#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from decimal import Decimal
from django.test import TestCase
from Sistema_proyecto.models import Cotizacion, Presupuesto
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

class TestPresupuestoModel(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(username="u", password="1234")

        self.cot = Cotizacion.objects.create(
            usuario=self.user,
            nombre="Cliente X",
            correo="x@test.com",
            servicio="Servicio A",
            descripcion="desc",
            fecha_entrega=date.today()
        )

    def test_creacion_presupuesto(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Empresa X",
            servicio="Mantenimiento",
            descripcion="Presupuesto general",
            monto_estimado=150000
        )

        self.assertEqual(p.cliente, "Empresa X")
        self.assertEqual(p.monto_estimado, 150000)
        self.assertIn("Presupuesto", str(p))

    def test_monto_negativo(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Empresa Y",
            servicio="ABC",
            descripcion="Desc",
            monto_estimado=-100
        )
        self.assertLess(p.monto_estimado, 0)

    def test_presupuesto_estado_default(self):
        p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Empresa X",
            servicio="Servicio Z",
            descripcion="ABC",
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

class TestPresupuestoViews(TestCase):

    def setUp(self):
        # usuario admin
        self.admin = User.objects.create_user(
            username="admin",
            password="123",
            is_staff=True
        )
        self.client.login(username="admin", password="123")

        # cotización válida
        self.cot = Cotizacion.objects.create(
            usuario=self.admin,
            nombre="Cliente Test",
            correo="cliente@test.com",
            servicio="Servicio X",
            descripcion="Desc",
            fecha_entrega=date.today() + timedelta(days=2),
            estado="aprobada"
        )

        # presupuesto inicial
        self.p = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente 1",
            servicio="Servicio 1",
            descripcion="Desc",
            monto_estimado=10000
        )

    # LISTA
    def test_lista_presupuestos(self):
        response = self.client.get(reverse("lista_presupuestos"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente 1")

    # CREAR
    def test_crear_presupuesto_post(self):
        data = {
            "cliente": "Nuevo Cliente",
            "servicio": "Nuevo Servicio",
            "descripcion": "Presupuesto creado",
            "monto_estimado": 55555
        }

        response = self.client.post(reverse("crear_presupuesto", args=[self.cot.id]), data)
        self.assertEqual(response.status_code, 200)


        nuevo = Presupuesto.objects.last()
        self.assertEqual(nuevo.cliente, "Cliente 1")
        self.p.refresh_from_db()
        self.assertEqual(self.p.monto_estimado, Decimal("10000"))



    # DETALLE
    def test_detalle_presupuesto(self):
        response = self.client.get(reverse("detalle_presupuesto", args=[self.p.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cliente 1")

    # EDITAR
    def test_editar_presupuesto_post(self):
        data = {
            "monto_total": 50000,
            "cliente": "Editado",
            "servicio": "Editado",
            "descripcion": "Editado",
            "monto_estimado": 77777
        }

        response = self.client.post(reverse("editar_presupuesto", args=[self.p.id]), data)
        self.assertEqual(response.status_code, 200)

        self.p.refresh_from_db()
        self.assertEqual(self.p.cliente, "Cliente 1")
        self.assertEqual(self.p.monto_estimado, Decimal("10000"))



