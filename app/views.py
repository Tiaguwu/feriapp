"""Vistas públicas de la aplicación de ferias."""

from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic.edit import CreateView
from django.db.models import Count


from datetime import date, timedelta
from .models import Categoria, Feria, Emprendedor, Visitante, Inscripcion
from .forms import EmprendedorForm, VisitanteForm, FeriaForm



class HomeView(TemplateView):
    """Vista de inicio con estadísticas generales."""

    template_name = "ferias/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas
        context['total_ferias_activas'] = Feria.objects.filter(activa=True).count()
        context['total_categorias'] = Categoria.objects.filter(activa=True).count()
        context['total_emprendedores'] = Emprendedor.objects.count()
        context['total_inscripciones'] = Inscripcion.objects.filter(estado="confirmada").count()
        
        # Ferias próximas (próximos 7 días)
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=7)
        context['ferias_proximas'] = Feria.objects.filter(
            activa=True,
            fecha_inicio__gte=hoy,
            fecha_inicio__lte=fecha_limite
        ).order_by('fecha_inicio')[:5]
        
        # Categorías con más ferias
        context['categorias_destacadas'] = Categoria.objects.annotate(
            total_ferias=Count('ferias')
        ).filter(total_ferias__gt=0).order_by('-total_ferias')[:5]
        
        return context


class ListaFeriasView(ListView):
    """Lista todas las ferias activas."""

    model = Feria
    template_name = "ferias/lista_ferias.html"
    context_object_name = "ferias"

    def get_queryset(self):
        """Retorna ferias activas, opcionalmente filtradas por categoría."""
        queryset = Feria.objects.filter(activa=True)
        
        categoria_id = self.request.GET.get('categoria')
        
        if categoria_id:
            queryset = queryset.filter(categorias__id=categoria_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Agrega la lista de categorías al contexto para mostrar en el template."""
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(activa=True)
        
        # Para mantener seleccionada la categoría actual en el selector
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            context['categoria_seleccionada'] = int(categoria_id)
        
        return context

    # --- EMPRENDEDOR ---

class ListaEmprendedorView(ListView):
    
    model = Emprendedor
    template_name = "emprendedores/lista_emprendedores.html"
    context_object_name = "emprendedores"

class DetalleEmprendedorView(DetailView):
    model = Emprendedor
    template_name = "emprendedores/detalle_emprendedor.html"
    context_object_name = "emprendedor"

class EmprendedorCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Emprendedor
    form_class = EmprendedorForm
    template_name = 'emprendedores/formulario_emprendedor.html'

    # Redirecciona a la lista de emprendedores cuando todo sale bien
    success_url = reverse_lazy('ferias:lista_emprendedores')
    success_message = "Emprendedor creado exitosamente."

    def form_valid(self, form):
        # Invocamos el save personalizado enviando al usuario logueado
        emprendedor = form.save(usuario=self.request.user)

        # Si el modelo encontró errores en validate(), retornará None
        if not emprendedor:
            # Renderiza de nuevo el formulario mostrando los non_field_errors
            return self.form_invalid(form)
    
        self.object = emprendedor
        return redirect(self.get_success_url())
    
    # Método para atajar a los duplicados
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'perfil_emprendedor'):
            # Si ya es emprendedor, lo mandamos a editar su perfil en vez de crear uno nuevo
            return redirect('ferias:editar_emprendedor', pk=request.user.perfil_emprendedor.pk)
        return super().dispatch(request, *args, **kwargs)

class EmprendedorUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Emprendedor
    form_class = EmprendedorForm
    template_name = 'emprendedores/formulario_emprendedor.html'
    success_url = reverse_lazy('ferias:lista_emprendedores')
    success_message = "Tus datos se actualizaron correctamente."

    def form_valid(self, form):
        emprendedor = self.get_object()  # Obtenemos el emprendedor que se está editando

        # Llamamos al método .update() del modelo pasándole los datos limpios del form
        errors = emprendedor.update(
            nombre=form.cleaned_data['nombre'],
            apellido=form.cleaned_data['apellido'],
            email=form.cleaned_data['email'],
            rubro=form.cleaned_data['rubro'],
            telefono=form.cleaned_data['telefono']
        )

        if errors:
            # Si el método update del modelo encuentra errores, los agregamos al form
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    # --- VISITANTE ---
class ListaVisitanteView(ListView):

    model = Visitante
    template_name = "visitantes/lista_visitantes.html"
    context_object_name = "visitantes"

class DetalleFeriaView(DetailView):
    model = Feria
    template_name = "ferias/detalle_feria.html"
    context_object_name = "feria"

class VisitanteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Visitante
    form_class = VisitanteForm
    template_name = 'visitantes/formulario_visitante.html'

    success_url = reverse_lazy('ferias:lista_visitantes')

    success_message = "Visitante creado exitosamente."

    def form_valid(self, form):
        visitante = form.save(usuario=self.request.user)

        if not visitante:
            return self.form_invalid(form)
        
        self.object = visitante
        return redirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'perfil_visitante'):

            return redirect('ferias:editar_visitante', pk=request.user.perfil_visitante.pk)
        return super().dispatch(request, *args, **kwargs)
    
class VisitanteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Visitante
    form_class = VisitanteForm
    template_name = 'visitantes/formulario_visitante.html'
    success_url = reverse_lazy('ferias:lista_visitantes')
    success_message = "Tus datos se actualizaron correctamente."

    def form_valid(self, form):
        visitante = self.get_object()

        errors = visitante.update(
            nombre=form.cleaned_data['nombre'],
            apellido=form.cleaned_data['apellido'],
            email=form.cleaned_data['email']
        )

        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    # --- USUARIO ---
class RegistroView(CreateView):
    template_name = 'registration/registro.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('elegir_rol')

    # Interceptamos el momento exacto en que el formulario es válido para loguearlo
    def form_valid(self, form):

        # Guarda al usuario en la base de datos
        # Al hacer form.save(), Django crea el User y lo asigna a self.object
        user = form.save()

        # Logueamos al usuario manualmente en la sesión actual
        login(self.request, user)

        # Redirigimos al success_url de forma segura
        return redirect(self.get_success_url())

class ElegirRolView(TemplateView):
    template_name = 'registration/elegir_rol.html'


class NuevaFeriaView(LoginRequiredMixin, CreateView):
    """
    Vista para crear una nueva feria.
    Requiere usuario autenticado.
    """
    form_class = FeriaForm
    template_name = "ferias/nueva_feria.html"
    success_url = reverse_lazy('app:lista_ferias')
    
    def form_valid(self, form):
        """
        Guarda la feria usando el método new() del modelo.
        El formulario ya validó los datos con Feria.validate()
        """
        cleaned_data = form.cleaned_data
        
        # Las categorías vienen como QuerySet del formulario
        categorias = cleaned_data.get('categorias')
        
        feria, errors = Feria.new(
            nombre=cleaned_data['nombre'],
            categorias=categorias,
            fecha_inicio=cleaned_data['fecha_inicio'],
            fecha_fin=cleaned_data['fecha_fin'],
            ubicacion=cleaned_data['ubicacion'],
            capacidad_puestos=cleaned_data['capacidad_puestos']
        )
        
        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
# TODO: implementar las siguientes vistas:
# class DetalleFeriaView(DetailView): ...
# class NuevaFeriaView(CreateView): ...
# class NuevaInscripcionView(CreateView): ...
# class CancelarInscripcionView(View): ...
