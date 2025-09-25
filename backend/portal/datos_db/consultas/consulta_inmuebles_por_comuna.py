import os
import django
import sys

sys.path.append("/usr/src/app")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto.settings")
django.setup()

from portal.models import Comuna, Inmueble

with open("/usr/src/app/portal/datos_db/consultas/inmuebles_por_comuna.txt", "w", encoding="utf-8") as f:
    for comuna in Comuna.objects.all().order_by("nombre"):
        f.write(f"Comuna: {comuna.nombre}\n")
        inmuebles = Inmueble.objects.filter(comuna=comuna).values("nombre", "descripcion")
        if inmuebles:
            for i in inmuebles:
                f.write(f"  - Nombre: {i['nombre']}\n    Descripción: {i['descripcion']}\n")
        else:
            f.write("  (Sin inmuebles)\n")
        f.write("\n")
print("Archivo 'inmuebles_por_comuna.txt' generado.")