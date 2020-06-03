from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import User, Product, Service_Messenger, Reservation

from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('username', 'email', 'last_login', 'is_vendedor', 'is_administrador',)
    list_filter = ('username', 'email', 'last_login', 'is_vendedor', 'is_administrador',)
    fieldsets = (
        (None, {'fields': ('username', 'email', )}),
        ('Permissions', {'fields': ('is_vendedor', 'is_administrador')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_vendedor', 'is_administrador')}
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Product)
admin.site.register(Service_Messenger)
admin.site.register(Reservation)
