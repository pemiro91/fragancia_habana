import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from Fragancia_Habana import settings

# Create your models here.
CATEGORIA_PERFUME = (
    ('Hombre', 'Hombre'),
    ('Mujer', 'Mujer')
)

TIPO_PERFUME = (
    ('Floral', 'Floral'),
    ('Frutal', 'Frutal'),
    ('Verde', 'Verde'),
    ('Aromatico', 'Aromatico'),
    ('Fougere', 'Fougere'),
    ('Citrico', 'Citrico'),
    ('Chipre', 'Chipre'),
    ('Amaderado', 'Amaderado'),
    ('Oriental', 'Oriental'),
    ('Musk', 'Musk')
)

HORARIO_ENTREGA = (
    ('8:00am-9:00am', '8:00am-9:00am'),
    ('9:00am-10:00am', '9:00am-10:00am'),
    ('10:00am-11:00am', '10:00am-11:00am'),
    ('11:00am-12:00m', '11:00am-12:00m'),
    ('12:00m-1:00pm', '12:00m-1:00pm'),
    ('1:00pm-2:00pm', '1:00pm-2:00pm'),
    ('2:00pm-3:00pm', '2:00pm-3:00pm'),
    ('3:00pm-4:00pm', '3:00pm-4:00pm'),
    ('4:00pm-5:00pm', '4:00pm-5:00pm'),
    ('5:00pm-6:00pm', '5:00pm-6:00pm'),
    ('6:00pm-7:00pm', '6:00pm-7:00pm'),
    ('7:00pm-8:00pm', '7:00pm-8:00pm')
)

ESTADO_ENTREGA = (
    ('Pendiente', 'Pendiente'),
    ('Cancelado', 'Cancelado'),
    ('Entregado', 'Entregado')
)
ESTADO_NOTIFICATION = (
    ('No-Leida', 'No Leida'),
    ('Leida', 'Leida'),
)
TIPO_NOTIFICATION = (
    ('Producto', 'Producto'),
    ('Reservacion', 'Reservacion'),
    ('Usuario', 'Usuario'),
)


class User(AbstractUser):
    is_vendedor = models.BooleanField(default=False)
    is_administrador = models.BooleanField(default=False)
    genero = models.CharField(max_length=15, choices=CATEGORIA_PERFUME)
    telefono = models.CharField(max_length=15, name='telefono')

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

    class Meta:
        permissions = (
            ("view_statistics", "Can view statistics"),
            ("assign_permissions_user", "Can assign permissions user"),
        )


class Product(models.Model):
    imagen = models.ImageField(upload_to='product_images/', null=True, blank=True)
    nombre = models.CharField(max_length=200, name='nombre')
    precio = models.CharField(max_length=50, name='precio')
    capacidad = models.CharField(max_length=50, name='capacidad')
    cantidad_disponible = models.IntegerField(name='cantidad_disponible')
    categoria = models.CharField(max_length=15, choices=CATEGORIA_PERFUME, name='categoria')
    tipo = models.CharField(max_length=50, name='tipo')

    def __str__(self):
        return self.nombre


class Reservation(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, name='producto')
    cantidad_producto = models.IntegerField(name='cantidad_producto')
    fecha_reservacion = models.DateField(default=datetime.datetime.now, name='fecha_reservacion')
    nombre = models.CharField(max_length=50, name='nombre', null=True, blank=True)
    direccion = models.TextField(name='direccion', null=True, blank=True)
    telefono = models.CharField(max_length=10, name='telefono', null=True, blank=True)
    fecha_entrega = models.CharField(max_length=50, name='fecha_entrega', null=True, blank=True)
    horario_entrega = models.CharField(max_length=50, choices=HORARIO_ENTREGA, name='horario_entrega',
                                       null=True, blank=True)

    def __str__(self): return str(self.producto)


class Estado_Reservation(models.Model):
    reservacion = models.ForeignKey(Reservation, on_delete=models.CASCADE, name='reservacion')
    estado = models.CharField(max_length=50, choices=ESTADO_ENTREGA, name='estado')
    fecha_estado = models.DateField()
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, name='vendedor')

    def __str__(self): return str(self.reservacion)


class Tipo_Perfume(models.Model):
    tipo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200)

    def __str__(self): return self.tipo


class Notification(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=300)
    estado = models.CharField(max_length=50, choices=ESTADO_NOTIFICATION, name='estado')
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICATION, name='tipo')
    fecha = models.DateTimeField(auto_now_add=True)

