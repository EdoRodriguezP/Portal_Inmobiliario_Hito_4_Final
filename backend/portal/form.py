from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory



class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = [
            "nombre",
            "descripcion",
            "m2_construidos",
            "m2_totales",
            "estacionamientos",
            "habitaciones",
            "banos",
            "direccion",
            "precio_mensual",
            "region",
            "comuna",
            "tipo_de_inmueble",
        ]
        widgets = {
            "region": forms.Select(attrs={"id": "id_region"}),
            "comuna": forms.Select(attrs={"id": "id_comuna"}),
        }

class SolicitudArriendoForm(forms.ModelForm):
    class Meta:
        model = SolicitudArriendo
        fields = ["mensaje"]

class PerfilUserForm(forms.ModelForm):
    class Meta:
        model = PerfilUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "rut",
            "imagen",
            "tipo_usuario",
        ]



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = PerfilUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "rut",
            "imagen",
            "tipo_usuario",
            "password1",
            "password2",
        ]

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

class ImagenInmuebleForm(forms.ModelForm):
    class Meta:
        model = ImagenInmueble
        fields = ['imagen', 'orden']

ImagenInmuebleFormSet = inlineformset_factory(
    Inmueble, ImagenInmueble,
    form=ImagenInmuebleForm,
    fields=['imagen', 'orden'],
    extra=1,
    max_num=8,
    can_delete=True
)
