from django import forms
from .models import Mensaje


class FormularioMensaje(forms.ModelForm):
    """Formulario para enviar un mensaje de contacto al administrador."""

    class Meta:
        model = Mensaje
        fields = ['asunto', 'cuerpo']
        labels = {
            'asunto': 'Asunto',
            'cuerpo': 'Mensaje',
        }
        widgets = {
            'asunto': forms.TextInput(attrs={'placeholder': '¿En qué podemos ayudarte?'}),
            'cuerpo': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Escribí tu mensaje aquí...'}),
        }
