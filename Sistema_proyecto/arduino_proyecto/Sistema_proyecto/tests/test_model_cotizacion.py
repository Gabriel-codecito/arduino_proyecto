#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from Sistema_proyecto.models import Cotizacion, validate_delivery_date
from django.core.exceptions import ValidationError
from datetime import date


class TestCotizacionModel(TestCase):

    def test_crear_cotizacion(self):
        fecha = timezone.now().date() + timedelta(days=1)

        cot = Cotizacion.objects.create(
            nombre="Juan",
            correo="juan@test.com",
            telefono="12345",
            empresa="P&U",
            servicio="Instalación eléctrica",
            descripcion="Test cotización",
            fecha_entrega=fecha
        )

        self.assertEqual(cot.estado, "pendiente")
        self.assertIn("Juan", str(cot))


class TestValidacionFecha(TestCase):

    def test_fecha_entrega_invalida(self):
        # Fecha anterior a HOY → debe fallar
        cot = Cotizacion(
            nombre="Juan",
            correo="juan@test.com",
            telefono="123",
            empresa="P&U",
            servicio="Servicio X",
            descripcion="desc",
            fecha_entrega=date.today() - timedelta(days=1)
        )

        with self.assertRaises(ValidationError):
            cot.full_clean()  # <-- AQUÍ se ejecuta validate_delivery_date

    def test_fecha_entrega_valida(self):
        cot = Cotizacion(
            nombre="Juan",
            correo="juan@test.com",
            telefono="123",
            empresa="P&U",
            servicio="Servicio X",
            descripcion="desc",
            fecha_entrega=date.today() + timedelta(days=1)
        )

        # No debe fallar
        cot.full_clean()