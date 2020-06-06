from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404

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
    if request.user.is_authenticated:
        product = get_object_or_404(Product, id=id_product)
        count_booking = request.POST.get('count_booking')
        name_service = request.POST.get('name_service')
        address_service = request.POST.get('address_service')
        phone_service = request.POST.get('phone_service')
        if count_booking:
            reserva = Reservation(
                producto_id=id_product,
                cantidad_producto=count_booking,
                vendedor_id=request.user.id,
                nombre=name_service,
                direccion=address_service,
                telefono=phone_service
            )
            reserva.save()
        else:
            messages.error(request, 'username or password not correct')
        context = {'product': product}
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
