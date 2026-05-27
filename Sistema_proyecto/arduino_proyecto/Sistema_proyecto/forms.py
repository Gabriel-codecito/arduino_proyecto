#AUTORES: Gabriel Aparicio y Jeaninne Aparicio – Proyecto IoT Puingenierías
#FECHA DE INICIO: 03-09-2024
#LICENCIA: Trabajo Académico – Distribución Restringida
#ÚLTIMA ACTUALIZACIÓN: 15-12-2025


import re
from django import forms
from django.contrib.auth import get_user_model
from .utils import validar_rut
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import  Cotizacion
from sensor.models import Sensor
from django.utils import timezone
from .models import (
    Herramienta,
    RegistroUsoHerramienta,
    OrdenTrabajo,
    Presupuesto,
    OrdenCompra,
    Factura,
    CondicionTaller,
    ReporteGenerado,
    ComentarioOT,
    Trabajador,
)
Usuario = get_user_model()

class RegistroJefaForm(UserCreationForm):
    rut = forms.CharField(max_length=8, required=True, label="RUT (sin DV)")
    dv = forms.CharField(max_length=1, required=True, label="DV")
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre")
    last_name = forms.CharField(required=True, label="Apellido")

    class Meta:
        model = Usuario
        fields = [
            "rut",
            "dv",
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned_data = super().clean()
        rut = cleaned_data.get("rut")
        dv = cleaned_data.get("dv")

        if rut and dv:
            dv_calc = self._calcular_dv(rut)
            if dv.upper() != dv_calc:
                raise ValidationError(f"El dígito verificador es incorrecto. Debe ser {dv_calc}")
        return cleaned_data

    def _calcular_dv(self, numero):
        suma = 0
        multiplicador = 2

        for digito in reversed(numero):
            suma += int(digito) * multiplicador
            multiplicador = 2 if multiplicador == 7 else multiplicador + 1

        resto = 11 - (suma % 11)
        return "K" if resto == 10 else "0" if resto == 11 else str(resto)

    def save(self, commit=True):
        user = super().save(commit=False)

        rut = self.cleaned_data.get("rut")
        dv = self.cleaned_data.get("dv").upper()
        user.RUT = f"{rut}-{dv}"

        user.rol = "admin"
        user.is_staff = True
        user.is_superuser = False  

        if commit:
            user.save()
        return user
    


class CotizacionForm(forms.ModelForm):
    class Meta:
        model = Cotizacion
        fields = [
            'nombre', 'correo', 'telefono', 'empresa',
            'servicio', 'descripcion', 'archivo',
            # fecha_entrega removido - se asigna en la vista
        ]
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'correo':      forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono':    forms.TextInput(attrs={'class': 'form-control'}),
            'empresa':     forms.TextInput(attrs={'class': 'form-control'}),
            'servicio':    forms.Select(attrs={'class': 'form-control premium-input', 'style': 'color: #000; background-color: #fff;'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean_archivo(self):  # ✅ nombre correcto
        archivo = self.cleaned_data.get("archivo")
        if archivo:
            if not archivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Solo se permiten archivos PDF.")
        return archivo
    


class HerramientaForm(forms.ModelForm):
    class Meta:
        model = Herramienta
        fields = ['nombre', 'descripcion', 'estado','sensor']
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            sensores = Sensor.objects.filter(herramienta__isnull=True)

            self.fields["sensor"].queryset = sensores

            # Agregar atributo data-estado dinámico
            for sensor in sensores:
                self.fields["sensor"].widget.choices.queryset = sensores
                self.fields["sensor"].widget.attrs.update({"class": "form-select"})

            # Necesitamos agregar data-estado en las opciones
            self.fields["sensor"].widget.choices = [
                (s.id, f"{s.tipo} (ID {s.id})") for s in sensores
            ]

class RegistroUsoHerramientaForm(forms.ModelForm):

    class Meta:
        model = RegistroUsoHerramienta
        fields = ['herramienta', 'orden_trabajo', 'fecha_inicio', 'fecha_fin']
        widgets = {
            "fecha_inicio": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
            "fecha_fin": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
class OrdenTrabajoForm(forms.ModelForm):
    class Meta:
        model = OrdenTrabajo
        fields = [ 'tecnico', 'descripcion', 'fecha_inicio', 'fecha_termino', 'estado', 'herramientas']
        widgets = {
            "estado": forms.Select(attrs={"class": "form-select estado-select"}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            "herramientas": forms.SelectMultiple(attrs={
                "class": "select2-multiple form-control",
                "style": "width:100%;"}),
            "fecha_inicio": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),
            "fecha_termino": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local"
                }
            ),
        }
        def clean(self):
            cleaned_data = super().clean()
            fecha_inicio = cleaned_data.get("fecha_inicio")
            fecha_termino = cleaned_data.get("fecha_termino")

            ahora = timezone.now()

            if fecha_inicio and fecha_inicio < ahora:
                self.add_error(
                    "fecha_inicio",
                    "La fecha de inicio no puede ser anterior a hoy."
                )

            if fecha_termino and fecha_termino < ahora:
                self.add_error(
                    "fecha_termino",
                    "La fecha de término no puede ser anterior a hoy."
                )

            if fecha_inicio and fecha_termino and fecha_termino <= fecha_inicio:
                self.add_error(
                    "fecha_termino",
                    "La fecha de término debe ser posterior a la fecha de inicio."
                )

            return cleaned_data


class PresupuestoForm(forms.ModelForm):
    class Meta:
        model = Presupuesto
        fields = [ "cliente", "servicio", "descripcion", "monto_base","herramienta"]
        widgets = {
            'monto_base': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'pattern': '[0-9]+',
                'inputmode': 'numeric',
                'placeholder': '0',
                'min': '0',
                'style': '''
                    background: rgba(255,255,255,0.05);
                    border: 2px solid rgba(212,175,55,0.4);
                    border-left: none;
                    border-radius: 0 10px 10px 0;
                    color: white;
                ''',
                'autocomplete': 'off',
            }),
        }
        def clean_monto_base(self):
            monto = self.cleaned_data['monto_base']
            # Eliminar puntos si alguien los pega
            monto = monto.replace('.', '').replace(',', '')
            if not monto.isdigit():
                raise forms.ValidationError("Ingrese solo números (CLP sin puntos ni comas).")
            return int(monto)



class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = [  'monto_total']
        widgets = {
            "monto_total": forms.TextInput(attrs={
                "type": "text",
                'inputmode': 'numeric',  # <-- Teclado numérico en móviles
                'pattern': '[0-9]+',     # <-- Solo números permitidos
                'placeholder': 'Ej: 100000',
                'autocomplete': 'off',
            })
        }

    def clean_monto_total(self):
        monto = self.cleaned_data.get("monto_total")

        # Convertir a string
        monto = str(monto)

        # Quitar separadores: puntos y comas
        monto = monto.replace(".", "").replace(",", "")

        try:
            return float(monto)
        except:
            raise forms.ValidationError("Ingresa un monto válido.")
    def __init__(self, *args, **kwargs):
        cotizacion_filtrada = kwargs.pop("cotizacion_filtrada", None)
        super().__init__(*args, **kwargs)

        # Si quieres ocultar el campo cotización o presupuesto:
        if "cotizacion" in self.fields:
            self.fields["cotizacion"].widget = forms.HiddenInput()

        if "presupuesto" in self.fields:
            self.fields["presupuesto"].widget = forms.HiddenInput()

        # Filtrar la cotización correcta:
        if cotizacion_filtrada:
            self.fields["cotizacion"].queryset = Cotizacion.objects.filter(id=cotizacion_filtrada.id)

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = [ 'archivo_cotizacion','archivo_presupuesto','archivo_oc','archivo_ot']


    def clean_monto_total(self):
        monto = self.cleaned_data.get("monto_total")

        # Convertir a string
        monto = str(monto)

        # Quitar separadores: puntos y comas
        monto = monto.replace(".", "").replace(",", "")

        try:
            return float(monto)
        except:
            raise forms.ValidationError("Ingresa un monto válido.")


class CondicionTallerForm(forms.ModelForm):
    class Meta:
        model = CondicionTaller
        fields = ['temperatura', 'humedad', 'vibracion']


class ReporteGeneradoForm(forms.ModelForm):
    class Meta:
        model = ReporteGenerado
        fields = ['tipo', 'archivo']


class ComentarioOTForm(forms.ModelForm):
    class Meta:
        model = ComentarioOT
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 2})
        }


class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = ['nombre', 'correo', 'telefono', 'herramientas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'herramientas': forms.CheckboxSelectMultiple(),
        }

class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = ['disponible']