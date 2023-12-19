from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import *


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),

    path('registro/', UserRegisterView.as_view(), name='user-register'),
    path('iniciarSesion/', UserLoginView.as_view(), name='user-login'),
    path('cerrarSesion/', UserLogout.as_view(), name='user-logout'),
]
