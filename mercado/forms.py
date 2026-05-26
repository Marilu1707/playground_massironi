from django import forms


class FormularioCanje(forms.Form):
    """Confirmación del canje de puntos por monedas."""
    confirmar = forms.BooleanField(
        required=True,
        label='Confirmo el canje de todos mis puntos disponibles (10 puntos = 5 monedas)',
    )
