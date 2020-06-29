import logging
import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rx.core.notification import Notification

from fragancia.models import Product, Reservation, User, Estado_Reservation, Tipo_Perfume, Notification

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
                return redirect('catalogue')
        else:
            messages.error(request, 'Usuario o contraseña incorrecto')
            return redirect('login')
    else:
        form = AuthenticationForm()
    return render(request, 'fragancia/login.html', {'form': form})


def logout(request):
    do_logout(request)
    return redirect('/')


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
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)

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
                   'cant_res_ord': cant_res_ord, 'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones
                   }
        return render(request, "fragancia/index.html", context)
    return redirect('login')


# -------------- Catalogo de Productos--------------#
@login_required(login_url='login')
def catalogue(request):
    if request.user.is_authenticated:
        list_product = Product.objects.all().exclude(cantidad_disponible=0)
        notificaciones = Notification.objects.all().order_by('-fecha').exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)

        return render(request, "fragancia/catalogo_productos.html",
                      {'list_product': list_product,
                       'notificaciones': notificaciones, 'cant_notificaciones': cant_notificaciones})
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

        notificaciones = Notification.objects.all().order_by('-fecha').exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)

        if count_booking:
            if int(count_booking) <= product.cantidad_disponible:
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

                Product.objects.filter(pk=id_product).update(cantidad_disponible=value_real)
                messages.success(request, 'Reserva realizada satisfactoriamente')

                # Agregando el mensaje de notificacion en la base de datos
                mensaje_notificacion = 'Reservó ' + count_booking + ' unidad(es) del producto: ' + product.nombre
                if mensaje_notificacion != '':
                    notificacion = Notification(mensaje=mensaje_notificacion, usuario=request.user,
                                                estado='No-Leido', tipo='Reservacion')
                    notificacion.save()
                return redirect(reverse('details_products', args=(id_product,)))
            else:
                messages.warning(request, 'La cantidad proporcionada es mayor que la disponible.')

        context = {'product': product, 'value_real': value_real, 'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones}
        return render(request, "fragancia/detalles_producto.html", context)
    return redirect('login')


# -------------- Gestionar productos--------------#
# -------------- Lista productos--------------#

def products(request):
    if request.user.is_authenticated:
        list_type_p = Tipo_Perfume.objects.all()
        list_products = Product.objects.all()
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)

        return render(request, "fragancia/listado_productos.html",
                      {'list_products': list_products, 'list_type_p': list_type_p,
                       'notificaciones': notificaciones, 'cant_notificaciones': cant_notificaciones})
    return redirect('login')


# -------------- Adicionar tipo de perfume--------------#
def add_type(request):
    if request.user.is_authenticated:
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        if request.method == 'POST':
            name_type = request.POST.get('name_type')
            description_type = request.POST.get('description_type')
            Tipo_Perfume.objects.create(
                tipo=name_type,
                descripcion=description_type
            )
            messages.success(request, "Tipo de producto registrado satisfactoriamente")
            return redirect('add_product')
        return render(request, 'fragancia/agregar_producto.html', {'notificaciones': notificaciones,
                                                                   'cant_notificaciones': cant_notificaciones})
    return redirect('login')


# -------------- Adicionar tipo de perfume editar--------------#
def add_type_edit(request, id_product):
    if request.user.is_authenticated:
        notificaciones_reserv = Notification.objects.all().exclude(usuario=request.user).exclude(
            mensaje__contains='Agregó')
        notificaciones_prod = Notification.objects.all().exclude(usuario=request.user).exclude(
            mensaje__contains='Realizó')
        cant_notificaciones = len(notificaciones_reserv) + len(notificaciones_prod)
        if request.method == 'POST':
            name_type = request.POST.get('name_type')
            description_type = request.POST.get('description_type')
            Tipo_Perfume.objects.create(
                tipo=name_type,
                descripcion=description_type
            )
            return redirect(reverse('edit_product', args=(id_product,)))
        return render(request, 'fragancia/editar_producto.html', {'notificaciones_reserv': notificaciones_reserv,
                                                                  'notificaciones_prod': notificaciones_prod,
                                                                  'cant_notificaciones': cant_notificaciones})
    return redirect('login')


# -------------- Adicionar producto--------------#
def add_product(request):
    if request.user.is_authenticated:
        list_type_p = Tipo_Perfume.objects.all()
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        lista_mensajes = []
        question_dict = {
            'types_perfumes': list_type_p,
            'notificaciones': notificaciones,
            'cant_notificaciones': cant_notificaciones,
            'lista_mensajes': lista_mensajes
        }
        if request.method == 'POST':
            name_product = request.POST.get('name_product')
            type_product = request.POST.get('type_product')
            category_product = request.POST.get('category_product')
            image_product = request.FILES['image_product']
            capacity_product = request.POST.get('capacity_product')
            price_product = request.POST.get('price_product')
            count_product = request.POST.get('count_product')

            producto = Product.objects.create(
                imagen=image_product,
                nombre=name_product,
                precio=price_product,
                capacidad=capacity_product,
                cantidad_disponible=count_product,
                categoria=category_product,
                tipo=type_product
            )

            # Agregando el mensaje de notificacion en la base de datos
            mensaje_notificacion = 'Agregó ' + count_product + ' unidad(es) del producto: ' + producto.nombre
            if mensaje_notificacion != '':
                notificacion = Notification(mensaje=mensaje_notificacion, usuario=request.user,
                                            estado='No-Leido', tipo='Producto')
                notificacion.save()
            messages.success(request, 'Producto agregado satisfactoriamente')
            return redirect('products')
        return render(request, 'fragancia/agregar_producto.html', question_dict)
    return redirect('login')


# -------------- Editar producto--------------#

def edit_product(request, id_product):
    if request.user.is_authenticated:
        product = Product.objects.get(id=id_product)
        list_type_p = Tipo_Perfume.objects.all()
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        lista_mensajes = []
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
            messages.success(request, 'Producto modificado satisfactoriamente')

            return redirect('products')
        context = {'product': product, 'types_perfumes': list_type_p,
                   'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones,
                   'lista_mensajes': lista_mensajes
                   }
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
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        context = {'list_users': list_users,
                   'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones,
                   }
        return render(request, 'fragancia/listado_usuarios.html', context)
    return redirect('login')


def user_profile(request):
    if request.user.is_authenticated:
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
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
        return render(request, "fragancia/editar_perfil_usuario.html",
                      {'notificaciones': notificaciones, 'cant_notificaciones': cant_notificaciones})
    return redirect('login')


def change_password(request):
    if request.user.is_authenticated:
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
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
            messages.success(request, 'Se cambió la contraseña satisfactoriamente')
            return redirect('login')
        context = {'notificaciones': notificaciones, 'cant_notificaciones': cant_notificaciones, }
        return render(request, "fragancia/cambiar_contrasena.html", context)
    return redirect('login')


def add_user(request):
    if request.user.is_authenticated:
        notificaciones = Notification.objects.all().order_by('-fecha').exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)

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

            if User.objects.filter(username=user_name).exists():
                messages.warning(request, 'El nombre de usuario ya existe')
                return redirect('add_user')
            elif password1 != password2:
                messages.warning(request, 'Las contraseñas no existen')
                return redirect('add_user')
            else:
                if tipo_perfil == 'vendedor':
                    user = User.objects.create_user(
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
                    user = User.objects.create_user(
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

            # Agregando el mensaje de notificacion en la base de datos
            mensaje_notificacion = 'Agregó al usuario: ' + user.username + ' al sistema'
            if mensaje_notificacion != '':
                notificacion = Notification(mensaje=mensaje_notificacion, usuario=request.user,
                                            estado='No-Leido', tipo='Usuario')
                notificacion.save()
            messages.success(request, 'Usuario registrado satisfactoriamente')
            return redirect('users')
        context = {'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones}
        return render(request, 'fragancia/agregar_usuario.html', context)
    return redirect('login')


def edit_user(request, id_user=None):
    if request.user.is_authenticated:
        user = get_object_or_404(User, id=id_user)
        user_custom = User.objects.get(id=id_user)
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            genero = request.POST.get('genero')
            user_name = request.POST.get('user_name')
            tipo_perfil = request.POST.get('tipo_perfil')
            password1 = request.POST.get('password1')
            with transaction.atomic():
                user_custom.set_password(password1)
                user_custom.save()
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
            messages.success(request, 'Datos de usuario actualizado satisfactoriamente')
            return redirect('users')
        context = {'user': user_custom,
                   'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones}
        return render(request, 'fragancia/editar_usuario.html', context)
    return redirect('login')


def delete_user(request, id_user):
    if request.user.is_authenticated:
        p = User.objects.get(id=id_user)
        p.delete()
        return redirect('users')
    return redirect('login')


# -------------- Asignar otros permisos--------------#

def assign_permissions(request, id_user):
    if request.user.is_authenticated:
        u = User.objects.get(id=id_user)
        # -------------------Comprobar permiso----------------------------------#
        perm_v_statistics = u.has_perm('fragancia.view_statistics')
        perm_a_permission = u.has_perm('fragancia.assign_permissions_user')
        # -----------------------------------------------------#
        content_type_user = ContentType.objects.get_for_model(User)
        # -----------------------------------------------------#
        if request.method == 'POST':
            ver_estadisticas = request.POST.get('view_statistics', False)
            agregar_permisos = request.POST.get('assign_permissions_user', False)

            # -----------------------------------------------------#
            permission_v_statis = Permission.objects.get(codename='view_statistics', content_type=content_type_user)
            permission_a_permission = Permission.objects.get(codename='assign_permissions_user',
                                                             content_type=content_type_user)

            if agregar_permisos:
                u.user_permissions.add(permission_a_permission)
            else:
                u.user_permissions.remove(permission_a_permission)
            # -----------------------------------------------------#
            if ver_estadisticas:
                u.user_permissions.add(permission_v_statis)
            else:
                u.user_permissions.remove(permission_v_statis)
            # -----------------------------------------------------#
            messages.success(request, 'Permisos asignados satisfactoriamnete')
            return redirect('users')
        context = {'perm_v_statistics': perm_v_statistics,
                   'perm_a_permission': perm_a_permission,
                   'usuario_select': u
                   }
        return render(request, 'fragancia/asignar_permisos.html', context)
    return redirect('login')


# --------------** Gestionar Reservaciones**--------------#
# -------------- Listar reservaciones--------------#

def reservations(request):
    if request.user.is_authenticated:
        list_reservations = Estado_Reservation.objects.filter(vendedor=request.user.id)
        list_reservations_admin = Estado_Reservation.objects.all()
        notificaciones = Notification.objects.all().exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        context = {'list_reservations': list_reservations,
                   'list_reservations_admin': list_reservations_admin,
                   'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones}
        return render(request, 'fragancia/listado_reservaciones.html', context)
    return redirect('login')


# -------------- Edit reservation--------------#

def edit_reservation(request, id_reservation=None):
    value_real = 0
    if request.user.is_authenticated:
        notificaciones = Notification.objects.all().order_by('-fecha').exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
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
                elif int(cantidad_reservada) <= reservation.cantidad_producto:
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
                messages.success(request, 'Reserva modificada satisfactoriamente')
                return HttpResponseRedirect(reverse('edit_reservation', args=(id_reservation,)))

            elif reservation.producto.cantidad_disponible == 0:
                messages.warning(request, 'La cantidad proporcionada es mayor que la disponible')
                return HttpResponseRedirect(reverse('edit_reservation', args=(id_reservation,)))
        context = {'reservation': reservation, 'value_real': value_real,
                   'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones}
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
        notificaciones = Notification.objects.all().order_by('-fecha').exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        reservation = get_object_or_404(Estado_Reservation, reservacion_id=id_reservation)
        context = {'reservation': reservation,
                   'notificaciones': notificaciones,
                   'cant_notificaciones': cant_notificaciones}
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
        messages.success(request, 'El estado de la Reservación se ha cambiado satisfactoriamente')
        return redirect('reservations')
    return redirect('login')


def messages_center(request):
    if request.user.is_authenticated:
        notificaciones = Notification.objects.all().order_by('-fecha').exclude(usuario=request.user)[:3]
        cant_notificaciones = len(notificaciones)
        todas_notificaciones = Notification.objects.all()

        context = {'notificaciones': notificaciones, 'todas_notificaciones': todas_notificaciones,
                   'cant_notificaciones': cant_notificaciones}
        return render(request, 'fragancia/listado_notificaciones.html', context)
    return redirect('login')


def delete_message(request, id_message):
    if request.user.is_authenticated:
        n = Notification.objects.get(id=id_message)
        n.delete()
        return redirect('messages_center')
    return redirect('login')
