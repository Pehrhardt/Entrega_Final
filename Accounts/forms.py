from django.contrib.auth.forms import UserChangeForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User,AbstractUser
from django.db import models
from django import forms
from .models import Avatar,Post

# Formulario Para crear nuevos usuarios utilizando el modelo definido por Django User
class RegistroUsuario(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2','last_name','first_name']

# Formulario para editar perfil
class UserEdit(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'last_name', 'first_name']

# Formulario para cambiar el Avatar
class AvatarForm(forms.ModelForm):
    class Meta:
        model = Avatar
        fields = '__all__'  # Esto incluirá todos los campos del modelo Avatar en el formulario

