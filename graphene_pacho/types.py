import graphene
from graphene_django.types import DjangoObjectType

from fragancia.models import User, Product, Service_Messenger, Reservation


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProductType(DjangoObjectType):
    class Meta:
        model = Product


class Service_MessengerType(DjangoObjectType):
    class Meta:
        model = Service_Messenger


class ReservationType(DjangoObjectType):
    class Meta:
        model = Reservation


class Query(object):
    all_users = graphene.List(UserType)
    all_productos = graphene.List(ProductType)
    all_servicio_mensajeria = graphene.List(Service_MessengerType)
    all_reservaciones = graphene.List(ReservationType)

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_all_productos(self, info, **kwargs):
        return Product.objects.all()

    def resolve_all_servicios(self, info, **kwargs):
        return Service_Messenger.objects.all()

    def resolve_all_reservaciones(self, info, **kwargs):
        return Reservation.objects.select_related('user').all()

    def resolve_reservacion(self, info, **kwargs):
        id = kwargs.get('id')
        vendedor = kwargs.get('vendedor')
        if id is not None:
            return Reservation.objects.select_related('user').get(pk=id)
        if vendedor is not None:
            return Reservation.objects.select_related('user').get(vendedor=vendedor)
        return None
