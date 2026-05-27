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
from Sistema_proyecto.models import Herramienta, RegistroUsoHerramienta, OrdenTrabajo

User = get_user_model()


class TestRegistroUsoHerramienta(TestCase):

    def setUp(self):
        self.client = Client()

        # Crear herramienta
        self.herramienta = Herramienta.objects.create(
            nombre="Taladro",
            descripcion="desc",
            estado="disponible"
        )

        # Crear OT
        self.ot = OrdenTrabajo.objects.create(
            cliente="Juan",
            servicio="soldadura",
            descripcion="desc",
            estado="pendiente"
        )
        self.registro = RegistroUsoHerramienta.objects.create(
            herramienta=self.herramienta,
            orden_trabajo=self.ot,
            fecha_inicio="2025-01-01 10:00"
        )
        # Staff para acceso
        self.user = User.objects.create_user(
            username="admin",
            password="1234",
            is_staff=True
        )
        self.client.login(username="admin", password="1234")


    # LISTA
    def test_lista_registros(self):
        response = self.client.get(reverse("lista_registros_uso"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Sistema_proyecto/herramientas/uso_lista.html")
        self.assertIn("registros", response.context)

    # DETALLE
    def test_detalle_registro(self):
        response = self.client.get(reverse("detalle_registro_uso", args=[self.registro.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Sistema_proyecto/herramientas/uso_detalle.html")

    # CREAR
    def test_crear_registro_get(self):
        response = self.client.get(reverse("crear_registro_uso"))
        self.assertEqual(response.status_code, 200)

    def test_crear_registro_post(self):
        response = self.client.post(reverse("crear_registro_uso"), {
            "herramienta": self.herramienta.id,
            "orden_trabajo": self.ot.id,
            "fecha_inicio": "2025-01-01 10:00",
            "energia_consumida": 2.5,
        })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Sistema_proyecto/herramientas/uso_crear.html")
        self.assertEqual(RegistroUsoHerramienta.objects.count(), 1)

    # EDITAR
    def test_editar_registro(self):
        reg = RegistroUsoHerramienta.objects.create(
            herramienta=self.herramienta,
            orden_trabajo=self.ot,
            fecha_inicio="2025-01-01 10:00"
        )

        response = self.client.post(
            reverse("editar_registro_uso", args=[reg.id]),
            {
                "herramienta": self.herramienta.id,
                "orden_trabajo": self.ot.id,
                "fecha_inicio": "2025-01-01 10:00",
                "fecha_fin": "2025-01-01 12:00",
                "energia_consumida": 3.0,
            }
        )

        self.assertEqual(response.status_code, 302)

    # ELIMINAR
    def test_eliminar_registro(self):
        response = self.client.post(reverse("eliminar_registro_uso", args=[self.registro.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(RegistroUsoHerramienta.objects.count(), 0)

    # PERMISOS
    def test_no_staff_no_accede(self):
        self.client.logout()
        user = User.objects.create_user(username="x", password="123", is_staff=False)
        self.client.login(username="x", password="123")

        response = self.client.get(reverse("lista_registros_uso"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)
