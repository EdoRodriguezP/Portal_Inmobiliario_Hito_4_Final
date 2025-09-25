from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from .models import Inmueble, ImagenInmueble
from .form import InmuebleForm, ImagenInmuebleForm
from django.forms import inlineformset_factory
from django.contrib import messages

ImagenInmuebleFormSet = inlineformset_factory(
    Inmueble, ImagenInmueble, form=ImagenInmuebleForm,
    fields=['imagen', 'orden'], extra=1, max_num=6, can_delete=True
)

@method_decorator(login_required, name="dispatch")
class PerfilInmuebleListView(ListView):
    model = Inmueble
    template_name = "perfil/inmueble_list.html"
    context_object_name = "inmuebles"
    paginate_by = 10
    def get_queryset(self): return Inmueble.objects.filter(propietario=self.request.user).order_by("-creado")

class PerfilInmuebleCreateView(LoginRequiredMixin, CreateView):
    model = Inmueble
    form_class = InmuebleForm
    template_name = "perfil/inmueble_form.html"
    success_url = reverse_lazy("perfil_inmueble_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ImagenInmuebleFormSet(self.request.POST, self.request.FILES, prefix='imageninmueble_set')
        else:
            context['formset'] = ImagenInmuebleFormSet(prefix='imageninmueble_set')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        form.instance.propietario = self.request.user
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.info(self.request, "Inmueble creado correctamente.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

@method_decorator(login_required, name="dispatch")
class PerfilInmuebleUpdateView(UpdateView):
    model = Inmueble
    form_class = InmuebleForm
    template_name = "perfil/inmueble_form.html"
    success_url = reverse_lazy("perfil_inmueble_list")

    def get_queryset(self):
        return Inmueble.objects.filter(propietario=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ImagenInmuebleFormSet(self.request.POST, self.request.FILES, instance=self.object, prefix='imageninmueble_set')
        else:
            context['formset'] = ImagenInmuebleFormSet(instance=self.object, prefix='imageninmueble_set')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        form.instance.propietario = self.request.user
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.info(self.request, "Inmueble actualizado correctamente.")
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
    


@method_decorator(login_required, name="dispatch")
class PerfilInmuebleDeleteView(DeleteView):
    model = Inmueble
    template_name = "perfil/inmueble_confirm_delete.html"
    success_url = reverse_lazy("perfil_inmueble_list")
    def get_queryset(self): return Inmueble.objects.filter(propietario=self.request.user)

    def form_valid(self, form):
        messages.info(self.request, "Inmueble eliminado correctamente.")
        return super().form_valid(form)

