"""Fragancia_Habana URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from graphene_file_upload.django import FileUploadGraphQLView

from fragancia import views
from django.contrib import admin
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.login, name="login"),
    path('index', views.index, name="index"),

    # Principal
    path('catalogue', views.catalogue, name="catalogue"),
    path('catalogue/<int:id_product>', views.details_products, name="details_products"),

    # Gestionar Productos
    path('products', views.products, name="products"),

    path('users', views.users, name="users"),
    path('user_profile', views.user_profile, name="user_profile"),

    # Api
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),

    path('', views.login_user, name="login"),

    path('', views.logout, name="logout"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
