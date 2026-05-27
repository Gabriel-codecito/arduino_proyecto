#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025

from django.test import TestCase
from Sistema_proyecto.models import Cotizacion, Presupuesto
from datetime import date, timedelta

class TestPresupuestoModel(TestCase):

    def setUp(self):
        self.cot = Cotizacion.objects.create(
            nombre="Cliente",
            empresa="Empresa X",
            correo="cx@cx.cl",
            telefono="123",
            servicio="Servicio",
            descripcion="desc",
            fecha_entrega=date.today(),
            estado="pendiente",
        )


    def test_crear_presupuesto(self):
        Presupuesto.objects.create(
        cotizacion=self.cot,
        cliente="Cliente",
        servicio="Servicio",
        descripcion="Presupuesto general",
        monto_estimado=150000
    )