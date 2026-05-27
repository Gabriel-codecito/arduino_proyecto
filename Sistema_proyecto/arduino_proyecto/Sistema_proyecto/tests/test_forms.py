#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#DESCRIPCIÓN GENERAL: Archivo de pruebas automatizadas destinado a verificar el correcto funcionamiento de los
#modelos, vistas y flujos críticos del sistema IoT–Web desarrollado para Puingenierías E.I.R.L.
#El objetivo es garantizar la estabilidad, integridad de datos y la trazabilidad del proceso administrativo .
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from Sistema_proyecto.forms import RegistroJefaForm
from datetime import date

Usuario = get_user_model()


class TestRegistroJefaForm(TestCase):

    def get_valid_data(self):
        return {
            "rut": "12345678",
            "dv": "5",
            "username": "jefa",
            "first_name": "Paula",
            "last_name": "González",
            "email": "paula@test.com",
            "password1": "ClaveSegura123",
            "password2": "ClaveSegura123",
        }

    # -------------------------------------------------------
    # 1) clean() – DV incorrecto → debe lanzar ValidationError
    # -------------------------------------------------------
    def test_clean_rut_dv_incorrecto(self):
        data = self.get_valid_data()
        data["dv"] = "9"  # incorrecto

        form = RegistroJefaForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("El dígito verificador es incorrecto", str(form.errors))

    # -------------------------------------------------------
    # 2) clean() – DV correcto → formulario válido
    # -------------------------------------------------------
    def test_clean_rut_dv_correcto(self):
        data = self.get_valid_data()

        form = RegistroJefaForm(data=data)

        self.assertTrue(form.is_valid())

    # -------------------------------------------------------
    # 3) _calcular_dv – cubrir ruta interna
    # -------------------------------------------------------
    def test_calcular_dv_funciona(self):
        form = RegistroJefaForm()

        # DV normal
        resultado = form._calcular_dv("12345678")
        self.assertEqual(resultado, "5")

        # DV = K (resto 10)
        resultado2 = form._calcular_dv("1000005")  # <-- ESTE FUNCIONA EN TU PROYECTO
        self.assertEqual(resultado2, "K")

        # DV = 0 (resto 11)
        resultado3 = form._calcular_dv("00000000")
        self.assertEqual(resultado3, "0")


    # -------------------------------------------------------
    # 4) save() – debe asignar RUT completo, rol y staff
    # -------------------------------------------------------
    def test_save_asigna_campos_correctamente(self):
        data = self.get_valid_data()
        form = RegistroJefaForm(data=data)

        self.assertTrue(form.is_valid())

        user = form.save()

        # RUT debe quedar como XXXXXXXXX-DV
        self.assertEqual(user.RUT, "12345678-5")

        # Debe quedar marcada como jefa/admin
        self.assertEqual(user.rol, "admin")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
