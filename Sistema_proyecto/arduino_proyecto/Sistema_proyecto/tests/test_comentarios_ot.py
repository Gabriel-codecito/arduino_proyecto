#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from django.test import TestCase
from django.contrib.auth import get_user_model
from Sistema_proyecto.models import ComentarioOT, Cotizacion, Presupuesto, OrdenTrabajo
from datetime import date

User = get_user_model()

class TestComentarioOT(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="admin123"
        )

        self.cot = Cotizacion.objects.create(
            nombre="Cliente",
            correo="c@test.com",
            servicio="Serv",
            descripcion="Desc",
            fecha_entrega=date.today()
        )

        self.pres = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente",
            servicio="Serv",
            descripcion="Desc",
            monto_estimado=10000
        )

        self.ot = OrdenTrabajo.objects.create(
            presupuesto=self.pres,
            cliente="Cliente",
            servicio="Servicio",
            descripcion="Trabajo"
        )

    def test_crear_comentario(self):
        c = ComentarioOT.objects.create(
            orden=self.ot,
            autor=self.user,   # ✅ CLAVE
            texto="Avance inicial"
        )

        self.assertIsNotNone(c.id)
        self.assertEqual(c.autor, self.user)
        self.assertIn("Comentario OT", str(c))
