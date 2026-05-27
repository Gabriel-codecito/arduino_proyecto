#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
import json

from mediciones.models import Medicion
from sensor.models import Sensor
from Sistema_proyecto.models import Herramienta, HistorialRFID
from mediciones.views import _mb_url

User = get_user_model()


#  API – LISTA MEDICIONES

class TestListaMediciones(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="admin",
            password="admin123",
            is_staff=True
        )
        self.client.login(username="admin", password="admin123")

        self.sensor = Sensor.objects.create(nombre="Sensor Test")

        Medicion.objects.create(
            sensor=self.sensor,
            voltaje=220,
            corriente=2,
            potencia=440,
            energia=1.5,
            costo=240
        )

    def test_lista_mediciones_ok(self):
        response = self.client.get(reverse("api_lista_mediciones"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(len(data) >= 1)
        self.assertIn("sensor", data[0])
        self.assertIn("voltaje", data[0])



#  INFORME DIARIO

class TestInformeDiario(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("admin", "a@a.com", "1234")
        self.client.login(username="admin", password="1234")

        self.sensor = Sensor.objects.create(nombre="SCT1")

        Medicion.objects.create(
            sensor=self.sensor,
            voltaje=10,
            corriente=2,
            potencia=20,
            energia=5,
            costo=50
        )

    def test_informe_diario_ok(self):
        response = self.client.get(reverse("informe_diario"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "Sistema_proyecto/administrador/informe_diario.html"
        )



#  API IoT – RECIBIR DATOS

class TestRecibirDatos(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse("recibir_datos")
        self.sensor = Sensor.objects.create(nombre="Sensor IoT")

    def test_recibir_datos_metodo_no_permitido(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_recibir_datos_falta_sensor_id(self):
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_recibir_datos_guarda_medicion(self):
        payload = {
            "sensor_id": self.sensor.id,
            "temperatura": 25,
            "humedad": 60,
            "corriente": 2,
            "energia": 1
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Medicion.objects.count(), 1)

    def test_recibir_datos_guarda_rfid(self):
        herramienta = Herramienta.objects.create(
            nombre="Taladro RFID",
            uid="3bb9bd2d",
            estado="disponible"
        )

        payload = {
            "sensor_id": self.sensor.id,
            "uid": "3BB9BD2D",
            "temperatura": 20
        }

        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(HistorialRFID.objects.count(), 1)

        registro = HistorialRFID.objects.first()
        self.assertEqual(registro.accion, "entrada")

        herramienta.refresh_from_db()
        self.assertEqual(herramienta.estado, "en_uso")



#  METABASE URL

class TestMetabaseURL(TestCase):

    def test_mb_url_invalido(self):
        settings.METABASE_SITE_URL = ""
        settings.METABASE_EMBEDDING_SECRET = ""
        url = _mb_url("dashboard", 1)
        self.assertIsNone(url)

    def test_mb_url_valido(self):
        settings.METABASE_SITE_URL = "http://test.com"
        settings.METABASE_EMBEDDING_SECRET = "secret123"

        url = _mb_url("dashboard", 1)
        self.assertTrue(url.startswith("http://test.com"))
        self.assertIn("dashboard", url)



#  ÚLTIMAS MEDICIONES

class TestUltimasMediciones(TestCase):

    def setUp(self):
        self.client = Client()
        self.sensor = Sensor.objects.create(nombre="SCT2")

        for _ in range(5):
            Medicion.objects.create(
                sensor=self.sensor,
                voltaje=10,
                corriente=1,
                potencia=10,
                energia=1,
                costo=100
            )

    def test_ultimas_mediciones_ok(self):
        response = self.client.get(reverse("api_ultimas_mediciones"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("mediciones", data)
        self.assertEqual(len(data["mediciones"]), 5)



#  PÁGINA MEDICIONES (PERMISOS)

class TestPaginaMediciones(TestCase):

    def setUp(self):
        self.client = Client()

    def test_anonymous_forbidden(self):
        response = self.client.get(reverse("pagina_mediciones"))
        self.assertEqual(response.status_code, 403)

    def test_staff_ok(self):
        staff = User.objects.create_user(
            username="staff",
            password="1234",
            is_staff=True
        )
        self.client.login(username="staff", password="1234")

        response = self.client.get(reverse("pagina_mediciones"))
        self.assertEqual(response.status_code, 200)



#  RESUMEN MENSUAL

class TestResumenMensual(TestCase):

    def setUp(self):
        self.client = Client()
        self.sensor = Sensor.objects.create(nombre="SCT9")

        Medicion.objects.create(
            sensor=self.sensor,
            voltaje=10,
            corriente=2,
            potencia=20,
            energia=5,
            costo=100
        )

    def test_resumen_mensual_ok(self):
        response = self.client.get(reverse("resumen_mensual"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "Sistema_proyecto/administrador/resumen_mensual.html"
        )



#  MEDICIONES DEL DÍA

class TestMedicionesDelDia(TestCase):

    def setUp(self):
        self.client = Client()
        self.sensor = Sensor.objects.create(nombre="SCT7")

        Medicion.objects.create(
            sensor=self.sensor,
            voltaje=11,
            corriente=2,
            potencia=22,
            energia=3,
            costo=30
        )

    def test_mediciones_del_dia_ok(self):
        response = self.client.get(reverse("mediciones_dia"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("mediciones", response.json())
