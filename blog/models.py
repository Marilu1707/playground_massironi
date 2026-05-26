from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.text import Truncator


class Post(models.Model):
    """Publicación del blog — recetas, lore y novedades del nido."""
    titulo = models.CharField(max_length=255)
    subtitulo = models.CharField(max_length=255, blank=True)
    cuerpo = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    imagen = models.ImageField(upload_to='posts/', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    precio_monedas = models.IntegerField(
        default=0,
        verbose_name='Precio en monedas (0 = gratis)',
        validators=[MinValueValidator(0)]
    )
    preview = models.TextField(blank=True, verbose_name='Preview público')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        """Genera preview automático con los primeros 200 chars del cuerpo."""
        if self.precio_monedas > 0 and self.cuerpo:
            self.preview = Truncator(self.cuerpo).chars(200)
        else:
            self.preview = ''
        super().save(*args, **kwargs)

    @property
    def es_premium(self):
        return self.precio_monedas > 0
