from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from .views import *


urlpatterns = [
    path('login/', obtain_auth_token),
    path('logout/', LogoutView.as_view()),
    path('getuser/', GetUserView.as_view()),
    path('register/', RegisterView.as_view()),

    path('home', Homepage.as_view(),name='homepage'),
    path('user-register', UserRegisterView.as_view(), name='user-register'),
    path('user-login', UserLoginView.as_view(), name='user-login'),
    path('registro/', UserRegisterView.as_view(), name='registro'),
]
