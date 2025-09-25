from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
from django.core.exceptions import ValidationError
from PIL import Image

# Create your models here.
class Region(models.Model):
    nro_region = models.CharField(max_length=5) #XVII
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.nro_region} {self.nombre}"   # Valparasio ||| numero de regios es : V

class Comuna(models.Model):
    nombre = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="comunas")

    def __str__(self):
        return f"{self.region} {self.nombre}"   # valparaiso ||| numero de region es : valparaiso
    


#modelo de inmueble 
class Inmueble(models.Model):
    
    class Tipo_de_inmueble(models.TextChoices):
        casa = "CASA", _("Casa")
        depto = "DEPARTAMENTO", _("Departamento")
        parcela = "PARCELA", _("Parcela")
    propietario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inmuebles", null=True, blank=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    m2_construidos = models.FloatField(default=0)
    m2_totales = models.FloatField(default=0)
    estacionamientos = models.PositiveSmallIntegerField(default=0)
    habitaciones = models.PositiveIntegerField(default=0)
    banos =  models.PositiveSmallIntegerField(default=0)
    direccion = models.CharField(max_length=100)
    precio_mensual = models.DecimalField(max_digits=8, decimal_places=0)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="inmuebles", null=True, blank=True)  # <-- Agregado
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, related_name="inmuebles")
    tipo_de_inmueble = models.CharField(max_length=20, choices=Tipo_de_inmueble.choices)


    def __str__(self):
        return f" {self.id} {self.propietario} {self.nombre}"



class SolicitudArriendo(models.Model):
    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = "P", _("Pendiente")
        ACEPTADA = "A", _("Aceptada")
        RECHAZADA = "R", _("Rechazada")

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name="solicitudes")
    arrendatario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name="solicitudes_enviadas", null=True, blank=True)
    mensaje = models.TextField()
    estado = models.CharField(max_length=10 , choices=EstadoSolicitud.choices,  default=EstadoSolicitud.PENDIENTE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.uuid} |  {self.inmueble} | {self.estado}"



class PerfilUser(AbstractUser):
    
    class TipoUsuario(models.TextChoices):
        ARRENDATARIO = "ARRENDATARIO", _("Arrendatario")
        ARRENDADOR = "ARRENDADOR", _("Arrendador")
    tipo_usuario = models.CharField(max_length=13, choices=TipoUsuario.choices, default=TipoUsuario.ARRENDATARIO)  
    rut = models.CharField(max_length=50, unique=True, blank=True, null=True)
    imagen = models.ImageField(upload_to='fotos_perfil/', default="default-profile.avif" )
                      
    def __str__(self):
        return f"{self.get_full_name()} | {self.tipo_usuario}"

class ImagenInmueble(models.Model):
    inmueble = models.ForeignKey(Inmueble, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='inmuebles/imagenes/')
    orden = models.PositiveIntegerField(default=0)

    

    def clean(self):
        # Máximo 8 imágenes por inmueble
        if self.inmueble_id and not self.pk:
            if self.inmueble.imagenes.count() >= 8:
                raise ValidationError("No se pueden subir más de 8 imágenes por inmueble.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Recorte automático
        
        if self.imagen:
            img_path = self.imagen.path
            img = Image.open(img_path)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            target_size = (1200, 1200)
            width, height = img.size
            aspect_ratio = width / height
            target_ratio = target_size[0] / target_size[1]
            if aspect_ratio > target_ratio:
                new_width = int(target_ratio * height)
                left = (width - new_width) // 2
                img = img.crop((left, 0, left + new_width, height))
            else:
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                img = img.crop((0, top, width, top + new_height))
            img = img.resize(target_size, Image.LANCZOS)
            img.save(img_path, format="JPEG", quality=90)
    
    def __str__(self):
        return f"Imagen de {self.inmueble.nombre} (Orden {self.orden})"