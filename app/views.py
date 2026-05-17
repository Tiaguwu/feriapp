"""Vistas públicas de la aplicación de ferias."""

from django.views.generic import ListView, TemplateView, DetailView

from .models import Feria
from .models import Emprendedor, Visitante


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

    # --- VISITANTE ---
class ListaVisitanteView(ListView):

    model = Visitante
    template_name = "visitantes/lista_visitantes.html"
    context_object_name = "visitantes"
# TODO: implementar las siguientes vistas:
# class DetalleFeriaView(DetailView): ...
# class NuevaFeriaView(CreateView): ...
# class NuevaInscripcionView(CreateView): ...
# class CancelarInscripcionView(View): ...
