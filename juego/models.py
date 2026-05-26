from django.db import models
from django.contrib.auth.models import User
from inventario.models import Queso


class Pedido(models.Model):
    """Pedido realizado por un usuario — vincula usuario, queso y progreso."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    queso = models.ForeignKey(Queso, on_delete=models.CASCADE, related_name='pedidos')
    cantidad = models.IntegerField(default=1, verbose_name='Cantidad')
    completado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)
    puntos_ganados = models.IntegerField(default=0)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"{self.usuario.username} pidió {self.cantidad}x {self.queso.nombre}"

    def calcular_puntos(self):
        """Otorga 5 puntos por unidad pedida."""
        return self.cantidad * 5
