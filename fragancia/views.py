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
    return render(request, 'fragancia/perfil_usuario.html', context)


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
    return render(request, 'fragancia/editar_productos.html', context)

# --------------** Gestionar productos**--------------#
# -------------- Listar usuarios--------------#
def users(request):
    context = {}
    return render(request, 'fragancia/listado_usuarios.html', context)

# -------------- Listar usuarios--------------#
def add_user(request):
    context = {}
    return render(request, 'fragancia/agregar_usuario.html', context)
