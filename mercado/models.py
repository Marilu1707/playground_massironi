from django.db import models
from django.contrib.auth.models import User
from blog.models import Post
from inventario.models import Queso


class Transaccion(models.Model):
    COMPRA_QUESO  = 'COMPRA_QUESO'
    COMPRA_RECETA = 'COMPRA_RECETA'
    VENTA_RECETA  = 'VENTA_RECETA'
    CANJE_PUNTOS  = 'CANJE_PUNTOS'
    JUEGO         = 'JUEGO'

    TIPO_CHOICES = [
        (COMPRA_QUESO,  'Compra de queso'),
        (COMPRA_RECETA, 'Compra de receta'),
        (VENTA_RECETA,  'Venta de receta'),
        (CANJE_PUNTOS,  'Canje de puntos'),
        (JUEGO,         'Premio del juego'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.IntegerField()  # positivo = ganó, negativo = gastó
    descripcion = models.CharField(max_length=255)
    referencia_queso = models.ForeignKey(
        Queso, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones'
    )
    referencia_post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones'
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'

    def __str__(self):
        return f"{self.usuario.username} — {self.get_tipo_display()} ({self.monto:+d})"


class CompraReceta(models.Model):
    comprador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recetas_compradas')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='compras')
    monto_pagado = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comprador', 'post')
        ordering = ['-fecha']
        verbose_name = 'Compra de receta'
        verbose_name_plural = 'Compras de recetas'

    def __str__(self):
        return f"{self.comprador.username} desbloqueó '{self.post.titulo}'"
