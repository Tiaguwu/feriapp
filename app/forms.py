from pyexpat import errors

from django import forms
from .models import Emprendedor, Inscripcion, Visitante, Feria, Categoria
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
    
    def save(self, usuario, commit=True):
        # Interceptamos el save para usar la lógica atómica del modelo
        if commit:
            # Invocamos el método de creación del modelo pasándole el usuario logueado
            emprendedor, errors = Emprendedor.new(
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                email=self.cleaned_data['email'],
                telefono=self.cleaned_data['telefono'],
                rubro=self.cleaned_data['rubro'],
                usuario=usuario
            )
            if errors:
                for error in errors:
                    self.add_error(None, error)  # Agrega errores no asociados a un campo específico
                return None
            return emprendedor
        return super().save(commit=commit)

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

    def save(self, usuario, commit=True):
        if commit:
            visitante, errors = Visitante.new(
                nombre=self.cleaned_data['nombre'],
                apellido=self.cleaned_data['apellido'],
                email=self.cleaned_data['email'],
                usuario=usuario
            )
            if errors:
                for error in errors:
                    self.add_error(None, error)
                return None
            return visitante
        return super().save(commit=commit)

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
    
class InscripcionForm(forms.ModelForm):
    """Formulario para inscribirse a una feria."""
    class Meta:
        model = Inscripcion
        fields = ['emprendedor', 'feria']
        widgets = {
            'emprendedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'feria': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

        labels = {
            'emprendedor': 'Emprendedor',
            'feria': 'Feria',
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Usar el usuario logueado para registrado_por
        self.usuario = usuario
        # Filtrar ferias para que solo se muestren las activas
        self.fields['feria'].queryset = Feria.objects.filter(activa=True)

        if usuario and (usuario.is_staff or usuario.is_superuser):
            self.fields['emprendedor'].queryset = Emprendedor.objects.all()
        else:
            self.fields.pop('emprendedor')  # Eliminar el campo si no es staff o superuser

    #  CONSULTA: es necesario el metodo clean() o la validación completa la hace la vista cuando llama a Inscripcion.new() ???

    def clean(self):
        cleaned_data = super().clean()
        emprendedor = cleaned_data.get('emprendedor')
        feria = cleaned_data.get('feria')

        if emprendedor is None:
            return cleaned_data # El usuario no es admin, no se valida el emprendedor en el front. Vale la pena validar lo demás?

        errors = Inscripcion.validate(emprendedor, feria, self.usuario)

        if errors:
            for error in errors:
                raise ValidationError(error)

        return cleaned_data