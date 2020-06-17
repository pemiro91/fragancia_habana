import logging
import os
from datetime import datetime
from pyexpat.errors import messages
from typing import re

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fragancia.models import *

logger = logging.getLogger(__name__)


# Create your views here.


def login_user(request):
    if request.POST:
        form = AuthenticationForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('index')
        else:
            messages.error(request, 'username or password not correct')
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'fragancia/login.html', {'form': form})


def logout(request):
    do_logout(request)
    return redirect('/')


@login_required(login_url='login')
def base(request):
    if request.user.is_authenticated:
        notificaciones = Notification.objects.filter(usuario=request.user)
        return render(request, "fragancia/base.html",{'notificaciones': notificaciones})
    return redirect('login')


# -------------- Index--------------#
@login_required(login_url='login')
def index(request):
    if request.user.is_authenticated:
        productos = Product.objects.all()
        cant_prod = len(productos)
        cant_prod_disp = 0
        vendedores = User.objects.filter(is_vendedor=True)
        cant_vendedores: int = len(vendedores)
        estado_reservaciones = Estado_Reservation.objects.all()
        cant_reservaciones: int = len(estado_reservaciones)
        reservaciones_ordenadas = Estado_Reservation.objects.order_by('-fecha_estado')[:5]
        cant_res_ord = len(reservaciones_ordenadas)
        reservaciones_pendientes = []
        reservaciones_entregadas = []
        reservaciones_canceladas = []
        if productos:
            for p in productos:
                cant_prod_disp += p.cantidad_disponible
        if estado_reservaciones:
            for r in estado_reservaciones:
                if r.estado == 'Pendiente':
                    reservacion = get_object_or_404(Reservation, pk=r.id)
                    reservaciones_pendientes.append(reservacion)
                elif r.estado == 'Entregado':
                    reservacion = get_object_or_404(Reservation, pk=r.id)
                    reservaciones_entregadas.append(reservacion)
                else:
                    reservacion = get_object_or_404(Reservation, pk=r.id)
                    reservaciones_canceladas.append(reservacion)

        cant_reserv_pend = len(reservaciones_pendientes)
        cant_reserv_entreg = len(reservaciones_entregadas)
        cant_reserv_canc = len(reservaciones_canceladas)
        context = {'cant_prod_sistema': cant_prod, 'cant_reserv_pend': cant_reserv_pend,
                   'cant_reserv_entreg': cant_reserv_entreg, 'cant_reserv_canc': cant_reserv_canc,
                   'cant_vendedores': cant_vendedores, 'cant_prod_disp': cant_prod_disp,
                   'cant_reservaciones': cant_reservaciones, 'reservaciones_ordenadas': reservaciones_ordenadas,
                   'cant_res_ord': cant_res_ord}
        return render(request, "fragancia/index.html", context)
    return redirect('login')


# -------------- Catalogo de Productos--------------#
@login_required(login_url='login')
def catalogue(request):
    if request.user.is_authenticated:
        list_product = Product.objects.all()
        return render(request, "fragancia/catalogo_productos.html", {'list_product': list_product})
    return redirect('login')


# ---------Detalles de un producto------#
@login_required(login_url='login')
def details_products(request, id_product=None):
    value_real = 0
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=id_product)
        count_booking = request.POST.get('count_booking')
        name_service = request.POST.get('name_service')
        address_service = request.POST.get('address_service')
        phone_service = request.POST.get('phone_service')
        date_service = request.POST.get('date_service')
        time_service = request.POST.get('time_service')
        otros_usuarios = User.objects.exclude(username=request.user.username)

        if count_booking:
            if int(count_booking) < product.cantidad_disponible:
                value_real = product.cantidad_disponible - int(count_booking)
                with transaction.atomic():
                    reservacion = Reservation(
                        producto_id=id_product,
                        cantidad_producto=count_booking,
                        nombre=name_service,
                        direccion=address_service,
                        telefono=phone_service,
                        fecha_entrega=date_service,
                        horario_entrega=time_service
                    )
                    reservacion.save()
                    estado_reservacion = Estado_Reservation(
                        reservacion=reservacion,
                        estado="Pendiente",
                        fecha_estado=datetime.now(),
                        vendedor_id=request.user.id,
                    )
                    estado_reservacion.save()

                if otros_usuarios:
                    for u in otros_usuarios:
                        usuario = get_object_or_404(pk=u.id)
                        usuario.userInfo.add_notification(request.user.first_name + 'Agregó una reservación de' + product.nombre)
                Product.objects.filter(pk=id_product).update(cantidad_disponible=value_real)

                return HttpResponseRedirect(reverse('details_products', args=(id_product,)))
            else:
                messages.error(request, 'La cantidad proporcionada es mayor que la disponible')
        context = {'product': product, 'value_real': value_real}
        return render(request, "fragancia/detalles_producto.html", context)
    return redirect('login')


# -------------- Gestionar productos--------------#
# -------------- Lista productos--------------#

def products(request):
    if request.user.is_authenticated:
        list_products = Product.objects.all()
        return render(request, "fragancia/listado_productos.html", {'list_products': list_products})
    return redirect('login')


# -------------- Adicionar producto--------------#

def add_product(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            name_product = request.POST.get('name_product')
            type_product = request.POST.get('type_product')
            category_product = request.POST.get('category_product')
            image_product = request.FILES['image_product']
            capacity_product = request.POST.get('capacity_product')
            price_product = request.POST.get('price_product')
            count_product = request.POST.get('count_product')
            Product.objects.create(
                imagen=image_product,
                nombre=name_product,
                precio=price_product,
                capacidad=capacity_product,
                cantidad_disponible=count_product,
                categoria=category_product,
                tipo=type_product
            )
            return redirect('products')
        context = {}
        return render(request, 'fragancia/agregar_producto.html', context)
    return redirect('login')


# -------------- Editar producto--------------#

def edit_product(request, id_product):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id_product)
        if request.method == 'POST':
            name_products = request.POST.get('name_products')
            type_products = request.POST.get('type_products')
            category_products = request.POST.get('category_products')
            capacity_products = request.POST.get('capacity_products')
            price_products = request.POST.get('price_products')
            count_products = request.POST.get('count_products')
            Product.objects.filter(pk=id_product).update(
                nombre=name_products,
                precio=price_products,
                capacidad=capacity_products,
                cantidad_disponible=count_products,
                categoria=category_products,
                tipo=type_products
            )
            return redirect('products')
        context = {'product': product}
        return render(request, 'fragancia/editar_producto.html', context)
    return redirect('login')


# -------------- Eliminar producto--------------#

def delete_product(request, id_product):
    if request.user.is_authenticated:
        p = Product.objects.get(id=id_product)
        os.remove(p.imagen.path)
        p.delete()
        return redirect('products')
    return redirect('login')


# -------------- Gestionar usuarios--------------#

def users(request):
    if request.user.is_authenticated:
        list_users = User.objects.all().exclude(is_superuser=True)
        context = {'list_users': list_users}
        return render(request, 'fragancia/listado_usuarios.html', context)
    return redirect('login')


def user_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            nombre = request.POST.get('first_name')
            apellidos = request.POST.get('last_name')
            correo = request.POST.get('email')
            telefono = request.POST.get('phone')
            usuario = request.POST.get('username')
            User.objects.filter(pk=request.user.id).update(
                first_name=nombre,
                last_name=apellidos,
                email=correo,
                telefono=telefono,
                username=usuario,
            )
            return redirect('user_profile')
        return render(request, "fragancia/perfil_usuario.html", {})
    return redirect('login')


def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirmed_new_password = request.POST.get('confirmed_new_password')
            U = User.objects.get(username=request.user.username)
            if not U.check_password(old_password):
                error = "Contraseña Incorrecta."
                return render(request, "fragancia/cambiar_contrasena.html", {'error': error})
            if confirmed_new_password != new_password:
                error = "Las Contraseñas No Coinciden."
                return render(request, "fragancia/cambiar_contrasena.html", {'error': error})
            U.set_password(new_password)
            U.save()
            return redirect('login')
        context = {}
        return render(request, "fragancia/cambiar_contrasena.html", context)
    return redirect('login')


def add_user(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            genero = request.POST.get('genero')
            user_name = request.POST.get('user_name')
            tipo_perfil = request.POST.get('tipo_perfil')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 != password2:
                error = "Las Contraseñas No Coinciden."
                return render(request, "fragancia/agregar_usuario.html", {'error': error})
            else:
                if tipo_perfil == 'vendedor':
                    User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        telefono=phone,
                        username=user_name,
                        is_vendedor=True,
                        is_administrador=False,
                        genero=genero
                    )
                else:
                    User.objects.create_user(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password1,
                        telefono=phone,
                        username=user_name,
                        is_vendedor=False,
                        is_administrador=True,
                        genero=genero
                    )
                return redirect('users')
        # usuario = User.objects.get(pk=2)
        change_user = Permission.objects.get(codename='change_user')
        # permis = usuario.user_permissions.add(change_user)
        context = {}
        return render(request, 'fragancia/agregar_usuario.html', context)
    return redirect('login')


def edit_user(request, id_user=None):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=id_user)
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            genero = request.POST.get('genero')
            user_name = request.POST.get('user_name')
            tipo_perfil = request.POST.get('tipo_perfil')
            password1 = request.POST.get('password1')
            user_custom = User.objects.get(id=id_user)
            if tipo_perfil == 'vendedor':
                User.objects.filter(id=id_user).update(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    telefono=phone,
                    username=user_name,
                    is_vendedor=True,
                    is_administrador=False,
                    genero=genero
                )

            else:
                User.objects.filter(pk=id_user).update(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    telefono=phone,
                    username=user_name,
                    is_vendedor=False,
                    is_administrador=True,
                    genero=genero
                )
            user_custom.set_password(password1)
            user_custom.save()
            return redirect('users')
        context = {'user': user}
        return render(request, 'fragancia/editar_usuario.html', context)
    return redirect('login')


def delete_user(request, id_user):
    if request.user.is_authenticated:
        p = User.objects.get(id=id_user)
        p.delete()
        return redirect('users')
    return redirect('login')


# -------------- Asignar otros permisos--------------#

def assign_permissions(request):
    context = {}
    return render(request, 'fragancia/asignar_permisos.html', context)


# --------------** Gestionar Reservaciones**--------------#
# -------------- Listar reservaciones--------------#

def reservations(request):
    if request.user.is_authenticated:
        list_reservations = Estado_Reservation.objects.filter(vendedor=request.user.id)
        context = {'list_reservations': list_reservations}
        return render(request, 'fragancia/listado_reservaciones.html', context)
    return redirect('login')


# -------------- Edit reservation--------------#

def edit_reservation(request, id_reservation=None):
    value_real = 0
    if request.user.is_authenticated:
        reservation = get_object_or_404(Reservation, id=id_reservation)
        if request.method == "POST":
            cantidad_reservada = request.POST.get('cantidad_reservada')
            name_service = request.POST.get('name_service')
            address_service = request.POST.get('address_service')
            phone_service = request.POST.get('phone_service')
            date_service = request.POST.get('date_service')
            time_service = request.POST.get('time_service')

            if int(cantidad_reservada) == reservation.cantidad_producto:
                if request.POST.get('switchMessenger'):
                    Reservation.objects.filter(pk=id_reservation).update(
                        cantidad_producto=cantidad_reservada,
                        nombre=name_service,
                        direccion=address_service,
                        telefono=phone_service,
                        fecha_entrega=date_service,
                        horario_entrega=time_service
                    )
                    return redirect('reservations')
                else:
                    Reservation.objects.filter(pk=id_reservation).update(
                        cantidad_producto=cantidad_reservada,
                        nombre="",
                        direccion="",
                        telefono="",
                        fecha_entrega="",
                        horario_entrega=""
                    )
                    return redirect('reservations')

            elif int(cantidad_reservada) <= reservation.producto.cantidad_disponible:
                if int(cantidad_reservada) > reservation.cantidad_producto:
                    value_add = int(cantidad_reservada) - reservation.cantidad_producto
                    value_real = reservation.producto.cantidad_disponible - value_add
                elif int(cantidad_reservada) < reservation.cantidad_producto:
                    value_sus = reservation.cantidad_producto - int(cantidad_reservada)
                    value_real = reservation.producto.cantidad_disponible + value_sus
                if request.POST.get('switchMessenger'):
                    Reservation.objects.filter(pk=id_reservation).update(
                        cantidad_producto=cantidad_reservada,
                        nombre=name_service,
                        direccion=address_service,
                        telefono=phone_service,
                        fecha_entrega=date_service,
                        horario_entrega=time_service
                    )
                else:
                    Reservation.objects.filter(pk=id_reservation).update(
                        cantidad_producto=cantidad_reservada,
                        nombre="",
                        direccion="",
                        telefono="",
                        fecha_entrega="",
                        horario_entrega=""
                    )

                Product.objects.filter(pk=reservation.producto.id).update(cantidad_disponible=value_real)
                return HttpResponseRedirect(reverse('edit_reservation', args=(id_reservation,)))

            elif int(cantidad_reservada) > reservation.producto.cantidad_disponible:
                messages.error(request, 'La cantidad proporcionada es mayor que la disponible')
        context = {'reservation': reservation, 'value_real': value_real}
        return render(request, 'fragancia/editar_reservacion.html', context)
    return redirect('login')


# -------------- Delete reservation--------------#

def delete_reservation(request, id_reservation):
    if request.user.is_authenticated:
        r = Reservation.objects.get(id=id_reservation)
        r.delete()
        return redirect('reservations')
    return redirect('login')


# -------------- Change State reservation--------------#

def change_state_reservation_init(request, id_reservation):
    if request.user.is_authenticated:
        reservation = get_object_or_404(Estado_Reservation, reservacion_id=id_reservation)
        context = {'reservation': reservation}
        return render(request, 'fragancia/editar_estado.html', context)
    return redirect('login')


def change_state_reservation(request, id_reservation):
    if request.user.is_authenticated:
        state_reservation = request.POST.get('state_reservation')
        Estado_Reservation.objects.filter(reservacion_id=id_reservation).update(
            estado=state_reservation,
            fecha_estado=datetime.now()
        )
        if state_reservation == 'Cancelado':
            r = Reservation.objects.get(id=id_reservation)
            product = Product.objects.get(pk=r.producto.id)
            value_real = product.cantidad_disponible + int(r.cantidad_producto)
            Product.objects.filter(pk=r.producto.id).update(cantidad_disponible=value_real)

        return redirect('reservations')
    return redirect('login')
