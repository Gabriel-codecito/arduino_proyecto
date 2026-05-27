#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase
from Sistema_proyecto.models import Cotizacion, Presupuesto, OrdenTrabajo
from datetime import date, timedelta

class TestOrdenTrabajoModel(TestCase):

    def setUp(self):
        self.cot = Cotizacion.objects.create(
            nombre="Cliente OT",
            correo="c@test.com",
            servicio="Serv",
            descripcion="Desc",
            fecha_entrega=date.today() + timedelta(days=1)
        )

        self.pres = Presupuesto.objects.create(
            cotizacion=self.cot,
            cliente="Cliente OT",
            servicio="Servicio",
            descripcion="Desc",
            monto_estimado=15000
        )

    def test_crear_ot(self):
        ot = OrdenTrabajo.objects.create(
            presupuesto=self.pres,
            cliente="Cliente OT",
            servicio="Soldadura",
            descripcion="Trabajo"
        )

        self.assertEqual(ot.estado, "pendiente")
        self.assertEqual(ot.servicio, "Soldadura")
