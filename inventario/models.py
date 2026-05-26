from django.db import models
from django.core.validators import MinValueValidator


class Queso(models.Model):
    """Producto del inventario del Nido Mozzarella."""
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    stock = models.IntegerField(default=0, verbose_name='Stock disponible')
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Precio ($)')
    precio_monedas = models.IntegerField(
        default=10,
        verbose_name='Precio en monedas 🪙',
        validators=[MinValueValidator(0)]
    )
    imagen = models.ImageField(upload_to='inventario/', null=True, blank=True)

    class Meta:
        verbose_name = 'Queso'
        verbose_name_plural = 'Quesos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def estado_stock(self):
        """Retorna el color del badge según el nivel de stock."""
        if self.stock >= 10:
            return 'green'
        elif self.stock >= 3:
            return 'orange'
        return 'red'

    def etiqueta_stock(self):
        if self.stock >= 10:
            return 'Disponible'
        elif self.stock >= 3:
            return 'Poco stock'
        return 'Sin stock'
