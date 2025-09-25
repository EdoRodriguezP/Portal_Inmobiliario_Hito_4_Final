from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DetailView
from django.urls import reverse_lazy
from .models import Inmueble, SolicitudArriendo, Comuna, PerfilUser
from .form import RegisterForm, LoginForm, PerfilUserForm, SolicitudArriendoForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin


# HOME: lista de inmuebles
class HomeInmuebleListView(ListView):
    model = Inmueble
    template_name = "web/home.html"
    context_object_name = "inmuebles"
    paginate_by = 12
    ordering = ["-creado"]

    def get_queryset(self):
        qs = super().get_queryset()
        tipo = self.request.GET.get("tipo")
        region = self.request.GET.get("region")
        comuna = self.request.GET.get("comuna")
        if tipo:
            qs = qs.filter(tipo_de_inmueble=tipo)
        if region:
            qs = qs.filter(region_id=region)
        if comuna:
            qs = qs.filter(comuna_id=comuna)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tipos"] = Inmueble.Tipo_de_inmueble.choices
        from .models import Region, Comuna
        ctx["regiones"] = Region.objects.all()
        ctx["comunas"] = Comuna.objects.all()
        ctx["selected_tipo"] = self.request.GET.get("tipo", "")
        ctx["selected_region"] = self.request.GET.get("region", "")
        ctx["selected_comuna"] = self.request.GET.get("comuna", "")
        return ctx

# AUTH
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "Has iniciado sesión.")
        return redirect("home")
    return render(request, "registration/login.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Has cerrado sesión.")
    return redirect("login")

# PERFIL (muestra enviadas/recibidas y botón a CRUD de inmuebles)
class PerfilView(TemplateView):
    template_name = "usuarios/perfil.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["enviadas"] = u.solicitudes_enviadas.select_related("inmueble", "inmueble__comuna").order_by("-creado")
        ctx["recibidas"] = (SolicitudArriendo.objects
                            .filter(inmueble__propietario=u)
                            .select_related("inmueble", "inmueble__comuna", "arrendatario")
                            .order_by("-creado"))
        return ctx

#class PerfilEditView(UpdateView):
 #   form_class = PerfilUserForm
  #  template_name = "usuarios/perfil.html"
   # success_url = reverse_lazy("perfil")
    #def get_object(self, queryset=None): return self.request.user

class PerfilEditView(LoginRequiredMixin, UpdateView):
    model = PerfilUser  
    form_class = PerfilUserForm
    template_name = "usuarios/perfil_edit.html"
    success_url = reverse_lazy("perfil")
    def get_object(self, queryset=None): return self.request.user

# CREAR SOLICITUD (muestra datos del inmueble)
class SolicitudArriendoCreateView(CreateView):
    model = SolicitudArriendo
    form_class = SolicitudArriendoForm
    template_name = "inmuebles/solicitud_form.html"
    success_url = reverse_lazy("perfil")

    def dispatch(self, request, *args, **kwargs):
        self.inmueble = get_object_or_404(Inmueble, pk=kwargs["inmueble_pk"])
        # Validación: no permitir que el propietario solicite su propio inmueble
        if self.inmueble.propietario == request.user:
            messages.info(request, "No puedes solicitar arriendo de tu propio inmueble.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["inmueble"] = self.inmueble
        return ctx

    def form_valid(self, form):
        solicitud = form.save(commit=False)
        solicitud.inmueble = self.inmueble
        solicitud.arrendatario = self.request.user
        solicitud.save()
        messages.success(self.request, "¡Solicitud enviada con éxito!")
        return redirect(self.success_url)
    


def _redir(request, fallback="perfil"):
    return request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse_lazy(fallback)

@login_required
@require_POST
def solicitud_aceptar(request, pk: int):
    s = get_object_or_404(SolicitudArriendo, pk=pk, inmueble__propietario=request.user)
    if s.estado != s.EstadoSolicitud.ACEPTADA:
        s.estado = s.EstadoSolicitud.ACEPTADA
        s.save(update_fields=["estado", "actualizado"])
        messages.success(request, "Solicitud aceptada.")
    else:
        messages.info(request, "La solicitud ya estaba aceptada.")
    return redirect(_redir(request))

@login_required
@require_POST
def solicitud_rechazar(request, pk: int):
    s = get_object_or_404(SolicitudArriendo, pk=pk, inmueble__propietario=request.user)
    if s.estado != s.EstadoSolicitud.RECHAZADA:
        s.estado = s.EstadoSolicitud.RECHAZADA
        s.save(update_fields=["estado", "actualizado"])
        messages.warning(request, "Solicitud rechazada.")
    else:
        messages.info(request, "La solicitud ya estaba rechazada.")
    return redirect(_redir(request))

@login_required
@require_POST
def solicitud_cancelar(request, pk: int):
    s = get_object_or_404(SolicitudArriendo, pk=pk, arrendatario=request.user)
    if s.estado == s.EstadoSolicitud.PENDIENTE:
        s.delete()
        messages.info(request, "Solicitud cancelada correctamente.")
    else:
        messages.warning(request, "Solo puedes cancelar solicitudes pendientes.")
    return redirect(_redir(request))

def comunas_por_region(request):
    region_id = request.GET.get("region_id")
    comunas = Comuna.objects.filter(region_id=region_id).values("id", "nombre")
    return JsonResponse(list(comunas), safe=False)

class InmuebleDetailView(DetailView):
    model = Inmueble
    template_name = "web/detalle_inmueble.html"
    context_object_name = "inmueble"
