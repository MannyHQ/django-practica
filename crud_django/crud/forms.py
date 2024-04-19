from django import forms 
from crud.models import Empleado, SolicitudServicio
from django.contrib.auth.models import User
class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre','correo','telefono']
        widgets = {'nombre': forms.TextInput(attrs={'class':'form-control'}),
                   'correo': forms.EmailInput(attrs={'class':'form-control'}),
                   'telefono': forms.TextInput(attrs={'class':'form-control'})
                   }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password']

class SolicitudServicioForm(forms.ModelForm):
    class Meta:
        model = SolicitudServicio
        fields = ['empresa','ocupacion','perfil_solicitud','estatus_solicitud']
        
