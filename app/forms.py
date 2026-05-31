from django import forms
from .models import Emprendedor, Visitante, Feria, Categoria
from django.core.exceptions import ValidationError

class EmprendedorForm(forms.ModelForm):

    # Se guarda lo de la izq porque es el value y
    # lo de la derecha es lo que se muestra en el select.
    RUBROS_CHOICES = [
        ('', 'Seleccione un rubro...'),  # Opción por defecto para obligar a elegir
        ('Artesanías', 'Artesanías y Manualidades'),
        ('Gastronomía', 'Gastronomía y Pastelería'),
        ('Indumentaria', 'Indumentaria y Textil'),
        ('Decoración', 'Decoración y Hogar'),
        ('Otros', 'Otros'),
    ]

    # Fuera del meta para que no sea un input de texto libre. 
    rubro = forms.ChoiceField(
        choices=RUBROS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rubro"
    )

    class Meta:
        model = Emprendedor
        fields = ['nombre', 'apellido', 'email', 'telefono', 'rubro']
        widgets = {
            'nombre': forms.TextInput(attrs ={'class': 'form-control', 'placeholder': 'Ingrese su nombre'}),
            'apellido': forms.TextInput(attrs= {'class': 'form-control', 'placeholder': 'Ingrese su apellido'}),
            'email': forms.EmailInput(attrs= {'class': 'form-control', 'placeholder': 'Ingrese su correo electronico'}),
            'telefono': forms.TextInput(attrs= {'class': 'form-control', 'placeholder': 'Ingrese su numero de telefono'}),
        }
    
    def clean_telefono(self):

        telefono = self.cleaned_data.get('telefono')
        if len(telefono) < 10:
            raise forms.ValidationError("El telefono debe tener al menos 10 dígitos.")
        
        if not telefono.isdigit():
            raise forms.ValidationError("El telefono solo puede contener numeros, sin espacios ni guiones.")
        
        return telefono

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nombre', 'apellido', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su nombre'}),
            'apellido': forms.TextInput(attrs= {'class': 'form-control', 'placeholder': 'Ingrese su apellido'}),
            'email': forms.EmailInput(attrs= {'class': 'form-control', 'placeholder': 'Ingrese su correo electronico'}),
        }

    # Validación para que el nombre y apellido no contengan números.
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            if any(char.isdigit() for char in nombre):
                raise forms.ValidationError("El nombre no puede contener números.")
        return nombre
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido:
            if any(char.isdigit() for char in apellido):
                raise forms.ValidationError("El apellido no puede contener números.")
        return apellido



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