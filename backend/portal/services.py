from .models import Comuna, Region


def imprimir_en_pantalla():
    regiones = Region.objects.all()
    for r in regiones:
        print(f"{r.id},{r.nro_region}, {r.nombre}")
        if hasattr(r, "comunas"):
            for s in r.comunas.all().order_by("nombre"):
                print(f" {s.id} {s.nombre}")

def crear_region(nro_region, nombre):
    region = Region(nro_region=nro_region, nombre=nombre)
    region.save()
    imprimir_en_pantalla()


def borrar_region(id):
    region = Region.objects.filter(id=id)
    region.delete()
    imprimir_en_pantalla()

""" def crear_comuna(region, nombre ):
    comuna_id = Comuna.objects.get(id=region)
    comuna = Comuna(comuna_id=comuna_id, nombre=nombre)
    comuna.save()
    return comuna """


def crear_comuna(region_id, nombre_comuna):
    try:
        # Obtener la región
        region = Region.objects.get(id=region_id)
    except Region.DoesNotExist:
        print(f"No existe la región con id {region_id}")
        return None

    # Crear o obtener la comuna
    comuna, created = Comuna.objects.get_or_create(
        nombre=nombre_comuna,
        region=region
    )

    if created:
        print(f"Comuna '{nombre_comuna}' creada exitosamente en la región {region.nombre}.")
    else:
        print(f"La comuna '{nombre_comuna}' ya existe en la región {region.nombre}.")

    return comuna


def borrar_comuna(comuna_id):
    comuna_id = Comuna.objects.filter(id=comuna_id)
    comuna_id.delete()
    imprimir_en_pantalla()