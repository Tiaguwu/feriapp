"""Rutas raíz del proyecto y delegación hacia la app principal."""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from app.views import ElegirRolView, RegistroView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls", namespace="ferias")),

    # Login y Logout
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Registro usuario
    path('registro/', RegistroView.as_view(), name='registro'),
    path('elegir-rol/', ElegirRolView.as_view(), name= 'elegir_rol'),
    
]
