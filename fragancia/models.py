import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from Fragancia_Habana import settings


# Create your models here.


class User(AbstractUser):
    is_vendedor = models.BooleanField(default=False)
    is_administrador = models.BooleanField(default=False)

    def get_perfil_vendedor(self):
        perfil_vendedor = None
        if hasattr(self, 'perfilvendedor'):
            perfil_vendedor = self.perfilvendedor
        return perfil_vendedor

    def get_perfil_administrador(self):
        perfil_administrador = None
        if hasattr(self, 'perfiladministrador'):
            perfil_administrador = self.perfiladministrador
        return perfil_administrador


class Product(models.Model):
    imagen = models.ImageField(upload_to='product_images')
    nombre = models.CharField(max_length=200, name='nombre')
    precio = models.CharField(max_length=50, name='precio')
    capacidad = models.CharField(max_length=50, name='capacidad')
    cantidad_disponible = models.IntegerField(name='cantidad_disponible')

    def __str__(self): return self.nombre


class Service_Messenger(models.Model):
    nombre = models.CharField(max_length=25, name='nombre')
    apellido = models.CharField(max_length=25, name='apellido')
    address = models.CharField(max_length=200, name='direccion')
    phone = models.CharField(max_length=20, name='telefono')
    time_ent = models.DateTimeField(max_length=50, name='horario_entrega')
    date_ent = models.DateField(max_length=50, name='fecha_entrega')

    def __str__(self):
        return self.nombre


class Reservation(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, name='producto')
    cantidad_producto = models.IntegerField(name='cantidad_producto')
    servicio_mensajeria = models.ForeignKey(Service_Messenger, on_delete=models.CASCADE, name='servicio_mensajeria')
    fecha_reservacion = models.DateField(default=datetime.datetime.now, name='fecha_reservacion')
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, name='vendedor')

    def __str__(self): return str(self.producto)
