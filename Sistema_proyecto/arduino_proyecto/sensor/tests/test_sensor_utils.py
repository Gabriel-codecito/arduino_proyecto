#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from unittest.mock import MagicMock
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from sensor.utils import staff_required


class TestStaffRequired(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_staff_ok(self):

        @staff_required
        def view(request):
            return HttpResponse("OK")

        req = self.factory.get("/")

        # Mock correcto: asignar atributos DESPUÉS de crear el objeto
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.is_staff = True
        req.user = mock_user

        resp = view(req)

        self.assertEqual(resp.status_code, 200)
