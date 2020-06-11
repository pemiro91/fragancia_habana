from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fragancia.models import Product, Reservation
import logging

logger = logging.getLogger(__name__)


# Create your views here.


def login_user(request):
    error = ''
    logout(request)
    if request.POST:
        form = AuthenticationForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/index')
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
        return render(request, "fragancia/base.html")
    return redirect('login')


# -------------- Index--------------#
@login_required(login_url='login')
def index(request):
    if request.user.is_authenticated:
        return render(request, "fragancia/index.html")
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
        if count_booking:
            if int(count_booking) <= product.cantidad_disponible:
                value_real = product.cantidad_disponible - int(count_booking)
                Reservation.objects.create(
                    producto_id=id_product,
                    cantidad_producto=count_booking,
                    vendedor_id=request.user.id,
                    nombre=name_service,
                    direccion=address_service,
                    telefono=phone_service,
                    fecha_entrega=date_service,
                    horario_entrega=time_service
                )
                Product.objects.filter(pk=id_product).update(cantidad_disponible=value_real)
                return HttpResponseRedirect(reverse('details_products', args=(id_product,)))
            else:
                messages.error(request, 'La cantidad proporcionada es mayor que la disponible')
        context = {'product': product, 'value_real': value_real}
        return render(request, "fragancia/detalles_producto.html", context)
    return redirect('login')


# -------------- Gestionar productos--------------#

def products(request):
    context = {}
    return render(request, 'fragancia/listado_productos.html', context)


# -------------- Gestionar usuarios--------------#

def users(request):
    context = {}
    return render(request, 'fragancia/listado_usuarios.html', context)


def user_profile(request):
    context = {}
    return render(request, 'fragancia/perfil_usuario.html', context)


# -------------- Asignar otros permisos--------------#

def assign_permissions(request):
    context = {}
    return render(request, 'fragancia/asignar_permisos.html', context)


# --------------** Gestionar Reservaciones**--------------#
# -------------- Listar reservaciones--------------#

def reservations(request):
    if request.user.is_authenticated:
        list_reservations = Reservation.objects.filter(vendedor=request.user.id)
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
                Reservation.objects.filter(pk=id_reservation).update(
                    cantidad_producto=cantidad_reservada,
                    nombre=name_service,
                    direccion=address_service,
                    telefono=phone_service,
                    fecha_entrega=date_service,
                    horario_entrega=time_service
                )
                return redirect('reservations')

            elif int(cantidad_reservada) <= reservation.producto.cantidad_disponible:
                if int(cantidad_reservada) > reservation.cantidad_producto:
                    value_add = int(cantidad_reservada) - reservation.cantidad_producto
                    value_real = reservation.producto.cantidad_disponible - value_add
                if int(cantidad_reservada) < reservation.cantidad_producto:
                    value_sus = reservation.cantidad_producto - int(cantidad_reservada)
                    value_real = reservation.producto.cantidad_disponible + value_sus
                Reservation.objects.filter(pk=id_reservation).update(
                    cantidad_producto=cantidad_reservada,
                    nombre=name_service,
                    direccion=address_service,
                    telefono=phone_service,
                    fecha_entrega=date_service,
                    horario_entrega=time_service
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
        product = Product.objects.get(pk=r.producto.id)
        value_real = product.cantidad_disponible + int(r.cantidad_producto)
        Product.objects.filter(pk=r.producto.id).update(cantidad_disponible=value_real)
        r.delete()
        return redirect('reservations')
    return redirect('login')
