from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import PerfilUsuario


class FormularioRegistro(UserCreationForm):
    """Formulario de registro de nuevo usuario."""
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'username': 'Nombre de usuario'}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email


class FormularioEditarPerfil(forms.ModelForm):
    """Formulario para editar datos del perfil de usuario."""
    first_name    = forms.CharField(max_length=50, required=False, label='Nombre')
    last_name     = forms.CharField(max_length=50, required=False, label='Apellido')
    email         = forms.EmailField(required=False, label='Email')
    eliminar_foto = forms.BooleanField(required=False, label='Eliminar foto de perfil actual')

    class Meta:
        model  = PerfilUsuario
        fields = ['foto_perfil', 'bio', 'link']
        labels = {
            'foto_perfil': 'Foto de perfil',
            'bio':         'Descripción',
            'link':        'Sitio web',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email


class FormularioCambiarPassword(PasswordChangeForm):
    """Formulario para cambiar la contraseña del usuario."""
    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']
