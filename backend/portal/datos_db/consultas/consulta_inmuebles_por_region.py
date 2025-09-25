import os
import django
import sys

sys.path.append("/usr/src/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto.settings")
django.setup()

from portal.models import Region, Inmueble

with open("/usr/src/app/portal/datos_db/consultas/inmuebles_por_region.txt", "w", encoding="utf-8") as f:
    for region in Region.objects.all().order_by("nombre"):
        f.write(f"Región: {region.nombre}\n")
        inmuebles = Inmueble.objects.filter(region=region).values("nombre", "descripcion")
        if inmuebles:
            for i in inmuebles:
                f.write(f"  - Nombre: {i['nombre']}\n    Descripción: {i['descripcion']}\n")
        else:
            f.write("  (Sin inmuebles)\n")
        f.write("\n")
print("Archivo 'inmuebles_por_region.txt' generado.")