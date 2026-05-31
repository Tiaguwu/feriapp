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



class FeriaForm(forms.ModelForm):
    """Formulario para crear/editar una feria."""
    
    class Meta:
        model = Feria
        fields = ['nombre', 'categorias', 'fecha_inicio', 'fecha_fin', 'ubicacion', 'capacidad_puestos']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la feria'
            }),
            'categorias': forms.SelectMultiple(attrs={
                'class': 'form-select'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Plaza Central, Salón Municipal'
            }),
            'capacidad_puestos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cantidad de puestos (mínimo 1)'
            }),
        }
        labels = {
            'nombre': 'Nombre de la feria',
            'categorias': 'Categorías',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'ubicacion': 'Ubicación',
            'capacidad_puestos': 'Capacidad de puestos',
        }
    
    def clean(self):
        """Validación a nivel de formulario usando el modelo."""
        cleaned_data = super().clean()
        
        nombre = cleaned_data.get('nombre')
        categorias = cleaned_data.get('categorias')  # QuerySet de Categoria
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        ubicacion = cleaned_data.get('ubicacion')
        capacidad_puestos = cleaned_data.get('capacidad_puestos')
        
        # Como validate() espera UNA categoría, tomamos la primera si existe
        # Esto es temporal hasta que se decida si se soportan múltiples categorías
        primera_categoria = categorias.first() if categorias and categorias.exists() else None
        
        errors = Feria.validate(
            nombre, primera_categoria, fecha_inicio, fecha_fin,
            ubicacion, capacidad_puestos
        )
        
        if errors:
            for error in errors:
                raise ValidationError(error)
        
        return cleaned_data