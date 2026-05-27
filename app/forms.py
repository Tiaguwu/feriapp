from django import forms
from .models import Emprendedor

class EmprendedorForm(forms.ModelForm):
    class Meta:
        model = Emprendedor
        fields = ['nombre', 'apellido', 'email', 'telefono']
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