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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView

from fragancia import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_user, name="login"),
    path('', views.logout, name="logout"),
    path('index', views.index, name="index"),

    # Principal
    path('catalogue', views.catalogue, name="catalogue"),
    path('catalogue/<int:id_product>', views.details_products, name="details_products"),

    # Gestionar Usuarios
    path('users', views.users, name="users"),
    path('user_profile', views.user_profile, name="user_profile"),
    path('change_password', views.change_password, name="change_password"),
    path('assign_permissions/<int:id_user>', views.assign_permissions, name="assign_permissions"),
    path('add_user', views.add_user, name="add_user"),
    path('edit_user/<int:id_user>', views.edit_user, name="edit_user"),
    path('delete_user/<int:id_user>', views.delete_user, name="delete_user"),

    # Gestionar Productos
    path('products', views.products, name="products"),
    path('add_product', views.add_product, name="add_product"),
    path('edit_product/<int:id_product>', views.edit_product, name="edit_product"),
    path('delete_product/<int:id_product>', views.delete_product, name="delete_product"),
    path('add_type', views.add_type, name="add_type"),
    path('add_type_edit/<int:id_product>', views.add_type_edit, name="add_type_edit"),

    # Gestionar Reservaciones
    path('reservations', views.reservations, name="reservations"),
    path('edit_reservation/<int:id_reservation>', views.edit_reservation, name="edit_reservation"),
    path('delete_reservation/<int:id_reservation>', views.delete_reservation, name="delete_reservation"),
    path('change_state_reservation_init/<int:id_reservation>', views.change_state_reservation_init,
         name="change_state_reservation_init"),
    path('change_state_reservation/<int:id_reservation>', views.change_state_reservation,
         name="change_state_reservation"),

    # Api
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path('delete_notification/<int:id_notification>', views.delete_notification, name="delete_notification"),

    # Gestionar Notificaciones
    path('notifications', views.notifications, name="notifications"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
