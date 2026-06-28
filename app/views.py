"""Vistas públicas de la aplicación de ferias."""

from django.contrib import messages
from django.views.generic import ListView, TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .mixins import EmprendedorRequiredMixin, VisitanteRequiredMixin
from datetime import date, timedelta
from django.db.models import Avg, Count

from .models import Categoria, Feria, Emprendedor, Resenia, Visitante, Inscripcion
from .forms import EmprendedorForm, ReseniaForm, VisitanteForm, FeriaForm, InscripcionForm

class HomeView(LoginRequiredMixin, TemplateView):
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

        # Datos para el gráfico de reseñas por feria según   por calificación
        resenias_por_feria = []
        for feria in Feria.objects.filter(activa=True, fecha_inicio__lte=date.today()):
            conteos = {i: 0 for i in range(1, 6)}
            for r in Resenia.objects.filter(feria=feria):
                conteos[r.calificacion] += 1
            resenias_por_feria.append({
                'nombre': feria.nombre,
                'conteos': [conteos[i] for i in range(1, 6)],
                'total': sum(conteos.values()),
            })
        context['resenias_por_feria'] = resenias_por_feria

        # Feriantes destacados
        context['feriantes_destacados'] = Emprendedor.objects.annotate(
            promedio = Avg('resenia__calificacion'),
            total_resenias = Count('resenia')
        ).filter(promedio__isnull=False).order_by('-promedio')[:4]

        return context

    # --- EMPRENDEDOR ---

class ListaEmprendedorView(LoginRequiredMixin, ListView):
    
    model = Emprendedor
    template_name = 'emprendedores/lista_emprendedores.html'
    context_object_name = 'emprendedores'

class DetalleEmprendedorView(LoginRequiredMixin, DetailView):
    model = Emprendedor
    template_name = 'emprendedores/detalle_emprendedor.html'
    context_object_name = 'emprendedor'

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
    success_url = reverse_lazy('ferias:mi_perfil')
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

class ListaVisitanteView(LoginRequiredMixin, ListView):

    model = Visitante
    template_name = 'visitantes/lista_visitantes.html'
    context_object_name = 'visitantes'

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
    success_url = reverse_lazy('ferias:mi_perfil')
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
class RegistroView(SuccessMessageMixin, CreateView):
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

    # --- FERIA ---

class NuevaFeriaView(LoginRequiredMixin, CreateView):
    """
    Vista para crear una nueva feria.
    Requiere usuario autenticado.
    """
    form_class = FeriaForm
    template_name = 'ferias/nueva_feria.html'
    success_url = reverse_lazy('ferias:lista_ferias')

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

        self.object = feria
        return redirect(self.success_url)

    def dispatch(self, request, *args, **kwargs):

        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "No tenés permisos para crear ferias.")
            return redirect('ferias:lista_ferias')

        return super().dispatch(request, *args, **kwargs)


class DetalleFeriaView(LoginRequiredMixin, DetailView):
    model = Feria
    template_name = 'ferias/detalle_feria.html'
    context_object_name = 'feria'

class ListaFeriasView(LoginRequiredMixin, ListView):
    """Lista todas las ferias activas."""

    model = Feria
    template_name = 'ferias/lista_ferias.html'
    context_object_name = 'ferias'

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

    # --- INSCRIPCIÓN ---

class NuevaInscripcionView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Inscripcion
    form_class = InscripcionForm
    template_name = 'inscripciones/nueva_inscripcion.html'
    success_url = reverse_lazy('ferias:mis_inscripciones')
    success_message = "Inscripción realizada exitosamente."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        feria = form.cleaned_data['feria']

        if self.request.user.is_staff or self.request.user.is_superuser:
            # Si es staff o superuser, puede inscribir a cualquier emprendedor
            emprendedor = form.cleaned_data['emprendedor']
        else:
            emprendedor = self.request.user.perfil_emprendedor

        inscripcion, errors = Inscripcion.new(
            emprendedor=emprendedor,
            feria=feria,
            registrado_por=self.request.user
        )

        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        self.object = inscripcion
        return redirect(self.get_success_url())

class MisInscripcionesView(LoginRequiredMixin, ListView):
    model = Inscripcion
    template_name = 'inscripciones/mis_inscripciones.html'
    context_object_name = 'inscripciones'

    def get_queryset(self):
        return Inscripcion.objects.filter(
            emprendedor=self.request.user.perfil_emprendedor
        )

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'perfil_emprendedor'):
            messages.error(request, "Debes ser un emprendedor para ver tus inscripciones.")
            return redirect('ferias:lista_ferias')
        return super().dispatch(request, *args, **kwargs)

class CancelarInscripcionView(LoginRequiredMixin, View):

    def post(self, request, pk):
        if request.user.is_staff or request.user.is_superuser: # Staff y superuser pueden cancelar cualquier inscripción
            inscripcion = get_object_or_404(Inscripcion, pk=pk)
        else:
            inscripcion = get_object_or_404(Inscripcion, pk=pk, emprendedor=request.user.perfil_emprendedor)

        errores = inscripcion.update(nuevo_estado='cancelada')
        if errores:
            messages.error(request, "No se pudo cancelar la inscripción: " + ", ".join(errores))
        else:
            messages.success(request, "Inscripción cancelada exitosamente.")
        return redirect('ferias:mis_inscripciones')

    # --- RESEÑAS ---

class ReseniaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Resenia
    form_class = ReseniaForm
    template_name = 'resenias/nueva_resenia.html'
    success_url = reverse_lazy('ferias:mis_resenias')
    success_message = "Reseña enviada exitosamente."

    # Protegemos la vista para que solo los visitantes puedan dejar reseñas
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'perfil_visitante'):
            messages.error(request, "Solo los visitantes pueden dejar una reseña.")
            return redirect('ferias:lista_ferias')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        visitante = self.request.user.perfil_visitante

        resenia, errors = Resenia.new(
            emprendedor = form.cleaned_data['emprendedor'],
            visitante = visitante,
            feria = form.cleaned_data['feria'],
            calificacion = form.cleaned_data['calificacion'],
            comentario = form.cleaned_data.get('comentario', ''),
        )

        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        self.object = resenia
        return redirect(self.get_success_url())

class MisReseniasView(LoginRequiredMixin, ListView):
    model = Resenia
    template_name = 'resenias/mis_resenias.html'
    context_object_name = 'resenias'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'perfil_visitante'):
            messages.error(request, "Solo los visitantes pueden dejar una reseña.")
            return redirect('ferias:lista_ferias')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Resenia.objects.filter(
            visitante=self.request.user.perfil_visitante
        )
    
class EliminarReseniaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.is_staff or request.user.is_superuser: # Staff y superuser pueden eliminar cualquier reseña
            resenia = get_object_or_404(Resenia, pk=pk)
        else:
            resenia = get_object_or_404(Resenia, pk=pk, visitante=request.user.perfil_visitante)
        resenia.delete()
        messages.success(request, "Reseña eliminada exitosamente.")
        return redirect('ferias:mis_resenias')