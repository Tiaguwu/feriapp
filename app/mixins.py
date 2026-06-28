from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class EmprendedorRequiredMixin(AccessMixin):
    """Verifica que el usuario tenga un perfil de emprendedor activo."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not hasattr(request.user, 'perfil_emprendedor'):
            messages.error(request, "Acceso denegado. Se requiere un perfil de Emprendedor.")
            return redirect('ferias:home')
        
        if request.user.perfil_emprendedor.pk != self.kwargs.get('pk'):
            messages.error(request, "Acceso denegado.")
            return redirect('ferias:home')

        return super().dispatch(request, *args, **kwargs)

class VisitanteRequiredMixin(AccessMixin):
    """Verifica que el usuario tenga un perfil de visitante activo."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_staff or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if not hasattr(request.user, 'perfil_visitante'):
            messages.error(request, "Acceso denegado. Se requiere un perfil de Visitante.")
            return redirect('ferias:home')

        if request.user.perfil_visitante.pk != self.kwargs.get('pk'):
            messages.error(request, "Acceso denegado.")
            return redirect('ferias:home')

        return super().dispatch(request, *args, **kwargs)

