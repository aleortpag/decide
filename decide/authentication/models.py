from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    nombre = models.CharField(max_length=50)
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username


# Cambiamos los nombres internos para evitar conflictos
Usuario._meta.get_field('groups').remote_field.related_name = 'usuario_groups'
Usuario._meta.get_field('user_permissions').remote_field.related_name = 'usuario_user_permissions'
