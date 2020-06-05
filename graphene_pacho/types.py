import graphene
from graphene import ObjectType
from graphene_django.types import DjangoObjectType

from fragancia.models import User, Product, Reservation
from django.db.models import Q


class UserType(DjangoObjectType):
    class Meta:
        model = User


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


class ReservationType(DjangoObjectType):
    class Meta:
        model = Reservation
        fields = '__all__'


def resolve_all_reservaciones_for_user(info, vendedor=None, **kwargs):
    user = info.context.user
    if user.is_anonymous:
        raise Exception('Authentication Failure!')
    return Reservation.objects.filter(vendedor_id=vendedor)


class Query(ObjectType):
    all_users = graphene.List(UserType)
    all_productos = graphene.List(ProductType)
    all_reservaciones = graphene.List(ReservationType, vendedor=graphene.Int())
    producto = graphene.Field(ProductType, id=graphene.Int())

    def resolve_producto(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Product.objects.get(pk=id)
        return None

    def resolve_all_users(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        return User.objects.all()

    def resolve_all_productos(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        return Product.objects.all()

    def resolve_all_reservaciones(self, info, vendedor=None, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        if vendedor:
            filter_v = (
                    Q(vendedor_id=vendedor)
            )
            return Reservation.objects.filter(filter_v)
        return Reservation.objects.all()

    def resolve_reservacion(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Authentication Failure!')
        id = kwargs.get('id')
        vendedor = kwargs.get('vendedor')
        if id is not None:
            return Reservation.objects.select_related('user').get(pk=id)
        if vendedor is not None:
            return Reservation.objects.select_related('user').get(vendedor=vendedor)
        return None
