from pyexpat import errors

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
    
    def __init__(self, *args, **kwargs):
        # Capturamos el usuario enviado desde la vista
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre and any(char.isdigit() for char in nombre):
            raise forms.ValidationError("El nombre no puede contener números.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido and any(char.isdigit() for char in apellido):
            raise forms.ValidationError("El apellido no puede contener números.")
        return apellido

    def clean_telefono(self):

        telefono = self.cleaned_data.get('telefono')
        if len(telefono) < 10:
            raise forms.ValidationError("El telefono debe tener al menos 10 dígitos.")
        
        if not telefono.isdigit():
            raise forms.ValidationError("El telefono solo puede contener numeros, sin espacios ni guiones.")
        
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellido = cleaned_data.get('apellido')
        email = cleaned_data.get('email')
        rubro = cleaned_data.get('rubro')
        telefono = cleaned_data.get('telefono')

        if not all([nombre, apellido, email, rubro, telefono]):
            return cleaned_data

        usuario_para_validar = self.instance.usuario if self.instance.pk else self.usuario

        errors = Emprendedor.validate(nombre, apellido, email, rubro, telefono, usuario_para_validar)

        if self.instance.pk and self.instance.email == email:
            errors = [e for e in errors if "Ya exise un emprendedor registrado con este email." not in e]

        if errors:
            raise ValidationError(errors)

        return cleaned_data

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nombre', 'apellido', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs= {'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs= {'class': 'form-control', 'placeholder': 'ejemplo@correo.com'}),
        }

    def __init__(self, *args, **kwargs):
        # Permitimos pasar el usuario logueado al formulario para usarlo en la validación y creación
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

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

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        apellido = cleaned_data.get('apellido')
        email = cleaned_data.get('email')

        # Si algun clean anterior fallo, detenemos la validacion cruzada 
        if not nombre or not apellido or not email:
            return cleaned_data

        # Identificamos qué usuario validar segun el contexto (Edicion vs Creacion)
        usuario_para_validar = self.instance.usuario if self.instance.pk else self.usuario

        # Validar como una capa de integridad
        errors = Visitante.validate(nombre, apellido, email, usuario_para_validar)

        if self.instance.pk and self.instance.email == email:
            errors = [e for e in errors if "Ya existe un visitante registrado con este email." not in e]

        if errors:
            raise ValidationError(errors)
        
        return cleaned_data

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
        cleaned_data = super().clean()
    
        nombre = cleaned_data.get('nombre')
        categorias = cleaned_data.get('categorias')  # QuerySet de Categoria
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        ubicacion = cleaned_data.get('ubicacion')
        capacidad_puestos = cleaned_data.get('capacidad_puestos')
    
        # Pasar todas las categorías a validate (no solo una)
        errors = Feria.validate(
            nombre, categorias, fecha_inicio, fecha_fin,
            ubicacion, capacidad_puestos
        )
    
        if errors:
            for error in errors:
                raise ValidationError(error)
    
        return cleaned_data