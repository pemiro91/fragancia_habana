from django.contrib import admin

# Register your models here.
from fragancia.models import Product, Service_Messenger, Reservation

admin.site.register(Product)
admin.site.register(Service_Messenger)
admin.site.register(Reservation)
