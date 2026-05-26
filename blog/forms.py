from django import forms
from .models import Post


class FormularioPost(forms.ModelForm):
    """Formulario para crear y editar posts del blog."""

    class Meta:
        model = Post
        fields = ['titulo', 'subtitulo', 'cuerpo', 'imagen', 'precio_monedas']
        labels = {
            'titulo': 'Título',
            'subtitulo': 'Subtítulo',
            'cuerpo': 'Contenido',
            'imagen': 'Imagen',
            'precio_monedas': 'Precio en monedas (0 = gratis)',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título de la receta o publicación'}),
            'subtitulo': forms.TextInput(attrs={'placeholder': 'Subtítulo opcional'}),
            'cuerpo': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Escribí el contenido aquí...'}),
            'precio_monedas': forms.NumberInput(attrs={'min': 0, 'placeholder': '0'}),
        }


class FormularioBusqueda(forms.Form):
    """Formulario de búsqueda de posts por título."""
    titulo = forms.CharField(
        max_length=255,
        required=False,
        label='',
        widget=forms.TextInput(attrs={'placeholder': '🔍 Buscar recetas...'}),
    )
