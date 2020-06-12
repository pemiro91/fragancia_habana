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
    ('8:00am-9:00am',   '8:00am-9:00am'),
    ('9:00am-10:00am',  '9:00am-10:00am'),
    ('10:00am-11:00am', '10:00am-11:00am'),
    ('11:00am-12:00m',  '11:00am-12:00m'),
    ('12:00m-1:00pm',   '12:00m-1:00pm'),
    ('1:00pm-2:00pm',   '1:00pm-2:00pm'),
    ('2:00pm-3:00pm',   '2:00pm-3:00pm'),
    ('3:00pm-4:00pm',   '3:00pm-4:00pm'),
    ('4:00pm-5:00pm',   '4:00pm-5:00pm'),
    ('5:00pm-6:00pm',   '5:00pm-6:00pm'),
    ('6:00pm-7:00pm',   '6:00pm-7:00pm'),
    ('7:00pm-8:00pm',   '7:00pm-8:00pm')
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


class Product(models.Model):
    imagen = models.ImageField(upload_to='product_images/', null=True, blank=True)
    nombre = models.CharField(max_length=200, name='nombre')
    precio = models.CharField(max_length=50, name='precio')
    capacidad = models.CharField(max_length=50, name='capacidad')
    cantidad_disponible = models.IntegerField(name='cantidad_disponible')
    categoria = models.CharField(max_length=15, choices=CATEGORIA_PERFUME, name='categoria')
    tipo = models.CharField(max_length=30, choices=TIPO_PERFUME, name='tipo')

    def __str__(self): return self.nombre

    def remove_on_image_update(self):
        try:
            # is the object in the database yet?
            obj = Product.objects.get(id=self.id)
        except Product.DoesNotExist:
            # object is not in db, nothing to worry about
            return
        # is the save due to an update of the actual image file?
        if obj.imagen and self.imagen and obj.imagen != self.imagen:
            # delete the old image file from the storage in favor of the new file
            obj.imagen.delete()

    def delete(self, *args, **kwargs):
        # object is being removed from db, remove the file from storage first
        self.imagen.delete()
        return super(Product, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # object is possibly being updated, if so, clean up.
        self.remove_on_image_update()
        return super(Product, self).save(*args, **kwargs)


class Reservation(models.Model):
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, name='producto')
    cantidad_producto = models.IntegerField(name='cantidad_producto')
    fecha_reservacion = models.DateField(default=datetime.datetime.now, name='fecha_reservacion')
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, name='vendedor')
    nombre = models.CharField(max_length=50, name='nombre', null=True, blank=True)
    direccion = models.TextField(name='direccion', null=True, blank=True)
    telefono = models.CharField(max_length=10, name='telefono', null=True, blank=True)
    fecha_entrega = models.CharField(max_length=50, name='fecha_entrega', null=True, blank=True)
    horario_entrega = models.CharField(max_length=50, choices=HORARIO_ENTREGA, name='horario_entrega',
                                       null=True, blank=True)

    def __str__(self): return str(self.producto)
