from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class EmprendedorRequiredMixin(AccessMixin):
    """Verifica que el usuario tenga un perfil de emprendedor activo."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not hasattr(request.user, 'perfil_emprendedor'):
            messages.error(request, "Acceso denegado. Se requiere un perfil de Emprendedor.")
            return redirect('ferias:home')
        
        return super().dispatch(request, *args, **kwargs)

class VisitanteRequiredMixin(AccessMixin):
    """Verifica que el usuario tenga un perfil de visitante activo."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not hasattr(request.user, 'perfil_visitante'):
            messages.error(request, "Acceso denegado. Se requiere un perfil de Visitante.")
            return redirect('ferias:home')

        return super().dispatch(request, *args, **kwargs)

