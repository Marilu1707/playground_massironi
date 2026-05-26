from django import forms
from .models import Pedido
from inventario.models import Queso


class FormularioPedido(forms.ModelForm):
    """Formulario para realizar un pedido de queso."""

    class Meta:
        model = Pedido
        fields = ['queso', 'cantidad']
        labels = {
            'queso': '¿Qué queso querés? 🧀',
            'cantidad': 'Cantidad',
        }
        widgets = {
            'queso': forms.Select(),
            'cantidad': forms.NumberInput(attrs={'min': 1, 'max': 20}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar quesos con stock disponible
        self.fields['queso'].queryset = Queso.objects.filter(stock__gt=0)
