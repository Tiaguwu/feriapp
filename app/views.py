"""Vistas públicas de la aplicación de ferias."""

from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import Feria, Emprendedor, Visitante
from .forms import EmprendedorForm


class HomeView(TemplateView):
    """Vista de inicio. Por ahora vacía — completar con estadísticas."""

    template_name = "ferias/home.html"


class ListaFeriasView(ListView):
    """Lista todas las ferias activas."""

    model = Feria
    template_name = "ferias/lista_ferias.html"
    context_object_name = "ferias"

    def get_queryset(self):
        """Retorna solo las ferias marcadas como activas."""
        return Feria.objects.filter(activa=True)

    # --- EMPRENDEDOR ---

class ListaEmprendedorView(ListView):
    
    model = Emprendedor
    template_name = "emprendedores/lista_emprendedores.html"
    context_object_name = "emprendedores"

class DetalleEmprendedorView(DetailView):
    model = Emprendedor
    template_name = "emprendedores/detalle_emprendedor.html"
    context_object_name = "emprendedor"

class EmprendedorCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Emprendedor
    form_class = EmprendedorForm
    template_name = 'emprendedores/formulario_emprendedor.html'

    # Redirecciona a la lista de emprendedores cuando todo sale bien
    success_url = reverse_lazy('ferias:lista_emprendedores')

    success_message = "Emprendedor creado exitosamente."

    def form_valid(self, form):
        # Asignamos el usuario que hizo la petición web (el que está logueado) 
        # a la instancia del emprendedor antes de guardarlo en la base de datos.
        form.instance.usuario = self.request.user
        
        return super().form_valid(form)
    
    # Método para atajar a los duplicados
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'emprendedor'):
            # Si ya es emprendedor, lo mandamos a editar su perfil en vez de crear uno nuevo
            return redirect('ferias:editar_emprendedor', pk=request.user.perfil_emprendedor.pk)
        return super().dispatch(request, *args, **kwargs)

class EmprendedorUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Emprendedor
    form_class = EmprendedorForm
    template_name = 'emprendedores/formulario_emprendedor.html'
    success_url = reverse_lazy('ferias:lista_emprendedores')
    success_message = "Los datos del emprendedor se actualizaron correctamente."

    # --- VISITANTE ---
class ListaVisitanteView(ListView):

    model = Visitante
    template_name = "visitantes/lista_visitantes.html"
    context_object_name = "visitantes"

class DetalleFeriaView(DetailView):
    model = Feria
    template_name = "ferias/detalle_feria.html"
    context_object_name = "feria"

# TODO: implementar las siguientes vistas:
# class DetalleFeriaView(DetailView): ...
# class NuevaFeriaView(CreateView): ...
# class NuevaInscripcionView(CreateView): ...
# class CancelarInscripcionView(View): ...
