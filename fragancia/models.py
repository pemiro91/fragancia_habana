from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, AbstractUser
from django.db import models
import datetime
from django.utils import timezone

from Fragancia_Habana import settings
from .managers import CustomUserManager


# Create your models here.


class CustomUser(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_administrator = models.BooleanField(default=False)


class Product(models.Model):
    image = models.ImageField(upload_to='product_images')
    name = models.CharField(max_length=200, name='nombre')
    price = models.CharField(max_length=50, name='precio')
    capacity = models.CharField(max_length=50, name='capacidad')
    count_dis = models.CharField(max_length=50, name='cantidad_disponible')

    def __str__(self): return self.name


class Service_Messenger(models.Model):
    name = models.CharField(max_length=50, name='nombre')
    last_name = models.CharField(max_length=50, name='npellido')
    address = models.CharField(max_length=200, name='direccion')
    phone = models.CharField(max_length=50, name='telefono')
    time_ent = models.CharField(max_length=50, name='horario_entrega')
    date_ent = models.DateField(max_length=50, name='fecha_entrega')

    def __str__(self):
        return self.name


class Reservation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, name='producto')
    count_prod = models.IntegerField(name='cantidad_producto')
    service_messenger = models.ForeignKey(Service_Messenger, on_delete=models.CASCADE, name='servicio_mensajeria')
    date_res = models.DateField(default=datetime.datetime.now, name='fecha_reservacion')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, name='vendedor')

    def __str__(self): return self.product
