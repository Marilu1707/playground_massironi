from django.db import models
from django.contrib.auth.models import User


class Mensaje(models.Model):
    """Mensaje de contacto enviado por un usuario al administrador."""
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    asunto = models.CharField(max_length=150)
    cuerpo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.remitente.username} — {self.asunto}"
