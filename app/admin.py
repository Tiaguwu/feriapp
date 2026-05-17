"""Configuración del panel de administración para la app principal."""

from django.contrib import admin
from .models import Feria, Visitante, Emprendedor

# TODO: reemplazar por @admin.register con list_display, list_filter, search_fields
@admin.register(Feria)
class FeriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'fecha_inicio', 'fecha_fin', 'ubicacion')
    list_filter = ('categoria', 'fecha_inicio')
    search_fields = ('nombre', 'ubicacion')

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