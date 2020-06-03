import graphene
from graphene_file_upload.scalars import Upload

from fragancia.models import *
from .types import *


class CreateProductMutation(graphene.Mutation):
    class Arguments:
        imagen = Upload(required=False)
        nombre = graphene.String(required=False)
        precio = graphene.Float(required=False)
        capacidad = graphene.String(required=False)
        cantidad_disponible = graphene.Int(required=False)

    nombre = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, **kwargs):
        imagen = kwargs.get('imagen', '')
        nombre = kwargs.get('nombre', '').strip()
        precio = kwargs.get('precio', 0)
        capacidad = kwargs.get('capacidad', '')
        cantidad_disponible = kwargs.get('cantidad_disponible', 0)

        obj = Product.objects.create(imagen=imagen, nombre=nombre, precio=precio,
                                     capacidad=capacidad, cantidad_disponible=cantidad_disponible)
        return CreateProductMutation(nombre=obj)


class Service_MessengerInput(graphene.InputObjectType):
    nombre_apellido = graphene.String()
    direccion = graphene.String()
    telefono = graphene.String()
    horario_entrega = graphene.DateTime()


class CreateReservacionMutation(graphene.Mutation):
    class Arguments:
        producto_id = graphene.Int()
        cantidad_producto = graphene.Int()
        input = Service_MessengerInput(required=True)
        vendedor_id = graphene.Int()

    reservacion = graphene.Field(ReservationType)

    @staticmethod
    def mutate(root, info, input=None):
        reservacion = Reservation(
            producto_id=input.producto_id,
            cantidad_producto=input.cantidad_producto,
            vendedor_id=input.vendedor_id)
        reservacion.save()
        return CreateReservacionMutation(reservacion=reservacion)


class Mutation(graphene.AbstractType):
    create_producto = CreateProductMutation.Field()
    create_reservacion = CreateReservacionMutation.Field()
