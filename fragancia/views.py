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


# --------------***** Tableros de Control *****--------------#
# -------------- Listar productos--------------#

def products(request):
    context = {}
    return render(request, 'fragancia/listado_productos.html', context)

# -------------- Listar usuarios--------------#
def users(request):
    context = {}
    return render(request, 'fragancia/listado_usuarios.html', context)
# -------------- Perfil de Usuario--------------#
def user_profile(request):
    context = {}
    return render(request, 'fragancia/perfil_usuario.html', context)