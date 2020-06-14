import graphql_jwt
from graphene_file_upload.scalars import Upload

from .types import *


class Service_MessengerInput(graphene.InputObjectType):
    nombre = graphene.String()
    direccion = graphene.String()
    telefono = graphene.String()
    fecha_entrega = graphene.String()
    horario_entrega = graphene.String()


class ProductInput(graphene.InputObjectType):
    nombre = graphene.String()
    precio = graphene.Float()
    capacidad = graphene.String()
    cantidad_disponible = graphene.Int()
    categoria = graphene.String()
    tipo = graphene.String()


class ReservacionInput(graphene.InputObjectType):
    cantidad_producto = graphene.Int()
    nombre = graphene.String()
    direccion = graphene.String()
    telefono = graphene.String()
    fecha_entrega = graphene.String()
    horario_entrega = graphene.String()


class CreateProductMutation(graphene.Mutation):
    class Arguments:
        imagen = Upload(required=False)
        input = ProductInput(required=True)

    ok = graphene.Boolean()
    producto = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        ok = True
        imagen = kwargs.get('imagen', '')
        producto_intance = Product(
            imagen=imagen,
            nombre=input.nombre,
            precio=input.precio,
            capacidad=input.capacidad,
            cantidad_disponible=input.cantidad_disponible,
            categoria=input.categoria,
            tipo=input.tipo)
        producto_intance.save()
        return CreateProductMutation(ok=ok, producto=producto_intance)


class CreateReservacionMutation(graphene.Mutation):
    class Arguments:
        producto_id = graphene.Int(required=True)
        cantidad_producto = graphene.Int(required=True)
        vendedor_id = graphene.Int(required=True)
        input = Service_MessengerInput(required=False)

    ok = graphene.Boolean()
    reservacion = graphene.Field(ReservationType)

    @staticmethod
    def mutate(root, info, input=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        ok = True
        producto_id = kwargs.get('producto_id', 0)
        cantidad_producto = kwargs.get('cantidad_producto', 0)
        vendedor_id = kwargs.get('vendedor_id', 0)
        reservacion = Reservation(
            producto_id=producto_id,
            cantidad_producto=cantidad_producto,
            vendedor_id=vendedor_id,
            nombre=input.nombre,
            direccion=input.direccion,
            telefono=input.telefono,
            fecha_entrega=input.fecha_entrega,
            horario_entrega=input.horario_entrega
        )
        reservacion.save()
        return CreateReservacionMutation(ok=ok, reservacion=reservacion)


class UpdateProducto(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ProductInput(required=True)

    ok = graphene.Boolean()
    producto = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, id, input=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        ok = False
        producto_instance = Product.objects.get(pk=id)
        if producto_instance:
            ok = True
            producto_instance.nombre = input.nombre
            producto_instance.precio = input.precio
            producto_instance.capacidad = input.capacidad
            producto_instance.cantidad_disponible = input.cantidad_disponible
            producto_instance.categoria = input.categoria
            producto_instance.tipo = input.tipo
            producto_instance.save()
            return UpdateProducto(ok=ok, producto=producto_instance)
        return UpdateProducto(ok=ok, producto=None)


class UpdateReservacion(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = ReservacionInput(required=True)

    ok = graphene.Boolean()
    reservacion = graphene.Field(ReservationType)

    @staticmethod
    def mutate(root, info, id, input=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        ok = False
        reservacion_instance = Reservation.objects.get(pk=id)
        if reservacion_instance:
            ok = True
            reservacion_instance.cantidad_producto = input.cantidad_producto
            reservacion_instance.nombre = input.nombre
            reservacion_instance.direccion = input.direccion
            reservacion_instance.telefono = input.telefono
            reservacion_instance.fecha_entrega = input.fecha_entrega
            reservacion_instance.horario_entrega = input.horario_entrega
            reservacion_instance.save()
            return UpdateReservacion(ok=ok, reservacion=reservacion_instance)
        return UpdateReservacion(ok=ok, reservacion=None)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = User.objects.get(pk=kwargs["id"])
        obj.delete()
        return cls(ok=True)


class DeleteReservacion(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = Reservation.objects.get(pk=kwargs["id"])
        obj.delete()
        return cls(ok=True)


class DeleteProducto(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        obj = Product.objects.get(pk=kwargs["id"])
        obj.delete()
        return cls(ok=True)


class Mutation(graphene.ObjectType):
    create_producto = CreateProductMutation.Field()
    create_reservacion = CreateReservacionMutation.Field()
    update_producto = UpdateProducto.Field()
    update_reservacion = UpdateReservacion.Field()
    delete_user = DeleteUser.Field()
    delete_reservacion = DeleteReservacion.Field()
    delete_producto = DeleteProducto.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
