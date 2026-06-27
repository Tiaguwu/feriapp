"""Definición de rutas públicas de la aplicación."""

from django.urls import path
from . import views

app_name = "ferias"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),

    path("ferias/", views.ListaFeriasView.as_view(), name="lista_ferias"),
    path("ferias/<int:pk>/", views.DetalleFeriaView.as_view(), name="detalle_feria"),
    path("ferias/nueva/", views.NuevaFeriaView.as_view(), name="nueva_feria"),

    path("emprendedores/", views.ListaEmprendedorView.as_view(), name="lista_emprendedores"),
    path("emprendedores/<int:pk>/", views.DetalleEmprendedorView.as_view(), name="detalle_emprendedor"),
    path('emprendedores/nuevo/', views.EmprendedorCreateView.as_view(), name='crear_emprendedor'),
    path('emprendedores/<int:pk>/editar/', views.EmprendedorUpdateView.as_view(), name='editar_emprendedor'),
    
    path("visitantes/", views.ListaVisitanteView.as_view(), name="lista_visitantes"),
    path("visitantes/nuevo/", views.VisitanteCreateView.as_view(), name="crear_visitante"),
    path("visitantes/<int:pk>/editar/", views.VisitanteUpdateView.as_view(), name="editar_visitante"),

    # TODO:
    
    path("inscripciones/nueva/", views.NuevaInscripcionView.as_view(), name="nueva_inscripcion"),
]
