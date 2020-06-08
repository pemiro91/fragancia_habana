from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from fragancia.models import Product, Reservation, User

import logging

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
            if int(count_booking) < product.cantidad_disponible:
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
    if request.user.is_authenticated:
        list_products = Product.objects.all()
        return render(request, "fragancia/listado_productos.html", {'list_products': list_products})
    return redirect('login')


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


def edit_product(request):
    context = {}
    return render(request, 'fragancia/editar_productos.html', context)


def delete_product(request, id):
    if request.user.is_anonymous():
        return HttpResponseRedirect('/')
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')
    c = cliente.objects.get(id=id)
    C = User.objects.get(username=c.user)
    C.delete()
    c.delete()
    return HttpResponseRedirect('/administrar/')


# -------------- Gestionar usuarios--------------#

def users(request):
    if request.user.is_authenticated:
        list_users = User.objects.all()
        return render(request, "fragancia/listado_usuarios.html", {'list_users': list_users})
    return redirect('login')


def add_user(request):
    usuario = User.objects.get(pk=2)
    change_user = Permission.objects.get(codename='change_user')
    permis = usuario.user_permissions.add(change_user)
    context = {'permis': permis}
    return render(request, 'fragancia/agregar_usuario.html', context)


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
