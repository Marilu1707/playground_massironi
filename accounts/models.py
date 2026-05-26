from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """Perfil extendido del usuario — One-to-One con User de Django."""
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    bio       = models.CharField(max_length=255, blank=True, verbose_name='Descripción')
    link      = models.URLField(blank=True, verbose_name='Sitio web')
    nivel     = models.IntegerField(default=1)
    puntos    = models.IntegerField(default=0)
    monedas   = models.IntegerField(default=100)

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def actualizar_nivel(self):
        """Calcula el nivel según los puntos acumulados."""
        if self.puntos >= 200:
            self.nivel = 5
        elif self.puntos >= 100:
            self.nivel = 4
        elif self.puntos >= 50:
            self.nivel = 3
        elif self.puntos >= 20:
            self.nivel = 2
        else:
            self.nivel = 1
        self.save()


@receiver(post_save, sender=User)
def create_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
