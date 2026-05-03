from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extensión del usuario de Django con atributo seller.
    """
    seller = models.BooleanField(default=False, help_text="Indica si el usuario es vendedor")
    alojamientos = models.JSONField(default=list, blank=True, verbose_name="Alojamientos", help_text="Lista de alojamientos del vendedor")
    actividades = models.JSONField(default=list, blank=True, verbose_name="Actividades", help_text="Lista de actividades del vendedor")
    restaurantes = models.JSONField(default=list, blank=True, verbose_name="Restaurantes", help_text="Lista de restaurantes del vendedor")
    planings = models.JSONField(default=list, blank=True, verbose_name="Plannings", help_text="Lista de planes de viaje del usuario")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.get_full_name() or self.username
