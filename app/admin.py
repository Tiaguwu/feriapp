"""Configuración del panel de administración para la app principal."""

from django.contrib import admin
from .models import Categoria, Feria, Inscripcion, Visitante, Emprendedor

@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mostrar_categorias', 'fecha_inicio', 'fecha_fin', 'ubicacion')
    list_filter = ('fecha_inicio',)  # Sacamos 'categoria' porque ManyToMany no se filtra igual
    search_fields = ('nombre', 'ubicacion')
    
    def mostrar_categorias(self, obj):
        """Muestra las categorías de la feria como lista separada por comas."""
        return ", ".join([c.nombre for c in obj.categorias.all()])
    mostrar_categorias.short_description = "Categorías"

@admin.register(Emprendedor)
class EmprendedorAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'rubro', 'email')
    list_filter = ('rubro',)
    search_fields = ('apellido', 'nombre', 'rubro', 'email')

@admin.register(Visitante)
class VisitanteAdmin(admin.ModelAdmin):
    list_display = ('apellido', 'nombre', 'email', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('apellido', 'nombre', 'email')

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('emprendedor', 'feria', 'fecha_inscripcion', 'estado')
    list_filter = ('emprendedor', 'feria', 'estado')
    search_fields = ('emprendedor__apellido', 'emprendedor__nombre', 'feria__nombre')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)