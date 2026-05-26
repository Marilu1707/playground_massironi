from django import forms
from .models import Queso


class FormularioQueso(forms.ModelForm):
    """Formulario para crear y editar quesos del inventario."""

    class Meta:
        model = Queso
        fields = ['nombre', 'descripcion', 'stock', 'precio', 'imagen']
        labels = {
            'nombre': 'Nombre del queso',
            'descripcion': 'Descripción',
            'stock': 'Cantidad en stock',
            'precio': 'Precio ($)',
            'imagen': 'Imagen',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Mozzarella fresca'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describí este queso...'}),
            'stock': forms.NumberInput(attrs={'min': 0}),
            'precio': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }


class FormularioBusquedaQueso(forms.Form):
    """Búsqueda de quesos por nombre."""
    nombre = forms.CharField(
        max_length=150,
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': '🔍 Buscar queso...'}),
    )
