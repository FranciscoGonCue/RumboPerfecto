from django.db import models


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.TextField(null=True, blank=True)
    email = models.TextField(unique=True, null=True, blank=True)
    password_hash = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'USUARIOS'

    def __str__(self):
        return self.nombre or f"Usuario {self.id_usuario}"
