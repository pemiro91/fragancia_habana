from django.shortcuts import render


# Create your views here.

# --------------***** Principal *****--------------#
# ----------------- Estadisticas-------------------#
def index(request):
    context = {}
    return render(request, 'fragancia/index.html', context)


# -------------- Catalogo de Productos--------------#
def catalogue(request):
    context = {}
    return render(request, 'fragancia/catalogo_productos.html', context)


# ---------------Detalles de un producto--------------#
def details_products(request):
    context = {}
    return render(request, 'fragancia/detalles_producto.html', context)


# -------------- Perfil de Usuario--------------#
def user_profile(request):
    context = {}
    return render(request, 'fragancia/editar_perfil_usuario.html', context)


# --------------***** Tableros de Control *****--------------#
# --------------** Gestionar productos**--------------#
# -------------- Listar productos--------------#

def products(request):
    context = {}
    return render(request, 'fragancia/listado_productos.html', context)

# -------------- Agregar producto--------------#

def add_product(request):
    context = {}
    return render(request, 'fragancia/agregar_producto.html', context)

# -------------- Editar producto--------------#

def edit_product(request):
    context = {}
    return render(request, 'fragancia/editar_producto.html', context)


# --------------** Gestionar usuarios**--------------#
# -------------- Listar usuarios--------------#
def users(request):
    context = {}
    return render(request, 'fragancia/listado_usuarios.html', context)


# -------------- Agregar usuarios--------------#
def add_user(request):
    context = {}
    return render(request, 'fragancia/agregar_usuario.html', context)


# -------------- Editar usuario--------------#
def edit_user(request):
    context = {}
    return render(request, 'fragancia/editar_usuario.html', context)


# -------------- Asignar otros permisos--------------#

def assign_permissions(request):
    context = {}
    return render(request, 'fragancia/asignar_permisos.html', context)


# --------------** Gestionar Reservaciones**--------------#
# -------------- Listar reservaciones--------------#

def reservations(request):
    context = {}
    return render(request, 'fragancia/listado_reservaciones.html', context)

# -------------- Listar reservaciones--------------#

def edit_reservation(request):
    context = {}
    return render(request, 'fragancia/editar_reservacion.html', context)
