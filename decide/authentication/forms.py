from django import forms
from django.forms.widgets import PasswordInput, TextInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ['username', 'nombre', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput())
    username.label = 'Nombre de usuario'
    password = forms.CharField(widget=PasswordInput())
    password.label = 'Contraseña'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
