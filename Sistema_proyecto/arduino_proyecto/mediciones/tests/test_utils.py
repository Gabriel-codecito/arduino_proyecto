#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025



from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from mediciones.utils import staff_required

User = get_user_model()


def dummy_view(request):
    return HttpResponse("OK")


class TestStaffRequired(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_no_autenticado(self):
        request = self.factory.get("/test")
        request.user = AnonymousUser()

        wrapped = staff_required(dummy_view)
        response = wrapped(request)

        self.assertEqual(response.status_code, 403)
        self.assertIn("Debe iniciar sesión", response.content.decode())

    def test_autenticado_no_staff(self):
        user = User.objects.create_user("user", "user@test.com", "1234")
        request = self.factory.get("/test")
        request.user = user

        wrapped = staff_required(dummy_view)
        response = wrapped(request)

        self.assertEqual(response.status_code, 403)
        self.assertIn("se requiere staff", response.content.decode())

    def test_autenticado_staff_ok(self):
        user = User.objects.create_user("admin", "a@a.com", "1234", is_staff=True)
        request = self.factory.get("/test")
        request.user = user

        wrapped = staff_required(dummy_view)
        response = wrapped(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")
