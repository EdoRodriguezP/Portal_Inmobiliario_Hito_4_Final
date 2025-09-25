import os
import django
import sys

sys.path.append("/usr/src/app")


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proyecto.settings")
django.setup()

from portal.models import PerfilUser

with open("/usr/src/app/portal/datos_db/consultas/usuarios_por_tipo.txt", "w", encoding="utf-8") as f:
    for tipo, tipo_display in PerfilUser.TipoUsuario.choices:
        f.write(f"Tipo de usuario: {tipo_display}\n")
        usuarios = PerfilUser.objects.filter(tipo_usuario=tipo).values("username", "first_name", "last_name", "password")
        if usuarios:
            for u in usuarios:
                f.write(f"  - Usuario: {u['username']}, Nombres: {u['first_name']} {u['last_name']}, Contraseña: {u['password']} \n")
        else:
            f.write("  (Sin usuarios)\n")
        f.write("\n")
print("Archivo 'usuarios_por_tipo.txt' generado.")