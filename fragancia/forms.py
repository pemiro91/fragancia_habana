from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('username', 'email', 'is_vendedor', 'is_superuser',)


class CustomUserChangeForm(UserChangeForm):
    is_superuser = forms.BooleanField(label='Es administrador', initial=False, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'is_vendedor', 'is_superuser',)
