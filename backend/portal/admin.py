from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.
@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_filter = ["region"]  
    search_fields = ["nombre"] 

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    search_fields = ["nombre", "nro_region"]
    list_display = ["nro_region", "nombre"]

class ImagenInmuebleInline(admin.TabularInline):
    model = ImagenInmueble
    extra = 1
    max_num = 6

@admin.register(Inmueble)
class InmuebleAdmin(admin.ModelAdmin):
    inlines = [ImagenInmuebleInline]

@admin.register(PerfilUser)
class PerfilUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Información extra", {"fields": ("rut", "tipo_usuario","imagen")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("rut", "tipo_usuario")}),
    )