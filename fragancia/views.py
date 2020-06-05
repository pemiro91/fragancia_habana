from django.shortcuts import render


# Create your views here.

def login(request):
    context = {}
    return render(request, 'fragancia/login.html', context)


def index(request):
    context = {}
    return render(request, 'fragancia/index.html', context)


# -------------- Catalogo de Productos--------------#
def catalogue(request):
    context = {}
    return render(request, 'fragancia/catalogo_productos.html', context)

# ---------Detalles de un producto------#
def details_products(request):
    context = {}
    return render(request, 'fragancia/detalles_producto.html', context)



# -------------- Gestionar productos--------------#

def products_list(request):
    context = {}
    return render(request, 'fragancia/listado_productos.html', context)
