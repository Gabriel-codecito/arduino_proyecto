#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase
from Sistema_proyecto.models import ReporteGenerado

class TestReporteGenerado(TestCase):

    def test_crear_reporte(self):
        r = ReporteGenerado.objects.create(
            tipo="Mediciones"
        )

        self.assertEqual(r.tipo, "Mediciones")
