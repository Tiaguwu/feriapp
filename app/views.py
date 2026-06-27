"""Vistas públicas de la aplicación de ferias."""

from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .mixins import EmprendedorRequiredMixin, VisitanteRequiredMixin

from .models import Categoria, Feria, Emprendedor, Visitante
from .forms import EmprendedorForm, VisitanteForm, FeriaForm


class HomeView(TemplateView):
    """Vista de inicio. Por ahora vacía — completar con estadísticas."""

    template_name = "ferias/home.html"

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

class ListaVisitanteView(ListView):

    model = Visitante
    template_name = "visitantes/lista_visitantes.html"
    context_object_name = "visitantes"

class DetalleFeriaView(DetailView):
    model = Feria
    template_name = "ferias/detalle_feria.html"
    context_object_name = "feria"

class DetalleEmprendedorView(DetailView):
    model = Emprendedor
    template_name = "emprendedores/detalle_emprendedor.html"
    context_object_name = "emprendedor"

class EmprendedorCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Emprendedor
    form_class = EmprendedorForm
    template_name = 'emprendedores/formulario_emprendedor.html'
    success_url = reverse_lazy('ferias:lista_emprendedores')
    success_message = "Emprendedor creado exitosamente." 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):

        nombre = form.cleaned_data['nombre']
        apellido = form.cleaned_data['apellido']
        email = form.cleaned_data['email']
        rubro = form.cleaned_data['rubro']
        telefono = form.cleaned_data['telefono']

        emprendedor, errors = Emprendedor.new(nombre, apellido, email, rubro, telefono, self.request.user)

        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)
    
        self.object = emprendedor

        messages.success(self.request, self.success_message)

        return redirect(self.get_success_url())
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'perfil_emprendedor'):
            return redirect('ferias:editar_emprendedor', pk=request.user.perfil_emprendedor.pk)
        return super().dispatch(request, *args, **kwargs)

class EmprendedorUpdateView(EmprendedorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Emprendedor
    form_class = EmprendedorForm
    template_name = 'emprendedores/formulario_emprendedor.html'
    success_url = reverse_lazy('ferias:lista_emprendedores')
    success_message = "Tus datos se actualizaron correctamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        emprendedor = self.get_object()

        errors = emprendedor.update(
            nombre=form.cleaned_data['nombre'],
            apellido=form.cleaned_data['apellido'],
            email=form.cleaned_data['email'],
            rubro=form.cleaned_data['rubro'],
            telefono=form.cleaned_data['telefono']
        )

        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        return super().form_valid(form)

    # --- VISITANTE ---

class VisitanteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Visitante
    form_class = VisitanteForm
    template_name = 'visitantes/formulario_visitante.html'
    success_url = reverse_lazy('ferias:lista_visitantes')
    success_message = "Visitante creado exitosamente."

    def get_form_kwargs(self):
        # Agrega el usuario actual en los parametros de inicializacion del form
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        apellido = form.cleaned_data['apellido']
        email = form.cleaned_data['email']

        # Ejecuta el método de creación personalizado del modelo, que retorna el visitante creado o None si hubo errores
        visitante, errors = Visitante.new(nombre, apellido, email, self.request.user)

        if errors:
            for error in errors:
                form.add_error(None, error) # Agrega el string directamente al formulario
            return self.form_invalid(form)

        self.object = visitante

        messages.success(self.request, self.success_message)

        return redirect(self.get_success_url())
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'perfil_visitante'):

            return redirect('ferias:editar_visitante', pk=request.user.perfil_visitante.pk)
        return super().dispatch(request, *args, **kwargs)
    
class VisitanteUpdateView(VisitanteRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Visitante
    form_class = VisitanteForm
    template_name = 'visitantes/formulario_visitante.html'
    success_url = reverse_lazy('ferias:lista_visitantes')
    success_message = "Tus datos se actualizaron correctamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs
    
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

        return super().form_valid(form)

    # --- USUARIO ---
class RegistroView(SuccessMessageMixin,CreateView):
    template_name = 'registration/registro.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('elegir_rol')
    success_message = "Tu cuenta fue creada exitosamente. ¡Te damos la bienvenida!"

    # Interceptamos el momento exacto en que el formulario es válido para loguearlo
    def form_valid(self, form):

        # Guarda al usuario en la base de datos
        # Al hacer form.save(), Django crea el User y lo asigna a self.object
        response = super().form_valid(form)

        # Logueamos al usuario manualmente en la sesión actual
        login(self.request, self.object)

        # Redirigimos al success_url de forma segura
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('ferias:home')
        return super().dispatch(request, *args, **kwargs)

class ElegirRolView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/elegir_rol.html'

    # Si intentan elegir rol sin estar logueados, los mandamos al login
    login_url = reverse_lazy('login')

class MiPerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/mi_perfil.html'

    # Si intenta acceder a su perfil sin estar logueado, lo mandamos al login
    login_url = reverse_lazy('login')

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
# class NuevaInscripcionView(CreateView): ...
# class CancelarInscripcionView(View): ...
