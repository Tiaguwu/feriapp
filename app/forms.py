from django import forms
from django.core.exceptions import ValidationError
from .models import Feria, Categoria


class FeriaForm(forms.Form):
    """Formulario para crear una nueva feria."""
    
    nombre = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activa=True),
        empty_label="Seleccione una categoría",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_inicio = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    fecha_fin = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    ubicacion = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    capacidad_puestos = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        """Validación a nivel de formulario usando el modelo."""
        cleaned_data = super().clean()
        
        nombre = cleaned_data.get('nombre')
        categoria = cleaned_data.get('categoria')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        ubicacion = cleaned_data.get('ubicacion')
        capacidad_puestos = cleaned_data.get('capacidad_puestos')
        
        # Usar el método validate del modelo Feria
        errors = Feria.validate(
            nombre, categoria, fecha_inicio, fecha_fin,
            ubicacion, capacidad_puestos
        )
        
        if errors:
            for error in errors:
                raise ValidationError(error)
        
        return cleaned_data