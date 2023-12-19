from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED,
        HTTP_400_BAD_REQUEST,
        HTTP_401_UNAUTHORIZED
)
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .forms import UserRegisterForm, UserLoginForm
from .serializers import UserSerializer
from django.contrib.auth import authenticate, login, logout


class GetUserView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        return Response(UserSerializer(tk.user, many=False).data)


class LogoutView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        try:
            tk = Token.objects.get(key=key)
            tk.delete()
        except ObjectDoesNotExist:
            pass

        return Response({})


class RegisterView(APIView):
    def post(self, request):
        key = request.data.get('token', '')
        tk = get_object_or_404(Token, key=key)
        if not tk.user.is_superuser:
            return Response({}, status=HTTP_401_UNAUTHORIZED)

        username = request.data.get('username', '')
        pwd = request.data.get('password', '')
        if not username or not pwd:
            return Response({}, status=HTTP_400_BAD_REQUEST)

        try:
            user = User(username=username)
            user.set_password(pwd)
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
        except IntegrityError:
            return Response({}, status=HTTP_400_BAD_REQUEST)
        return Response({'user_pk': user.pk, 'token': token.key}, HTTP_201_CREATED)

# ------------------------------------------------------------------------------------

class Homepage(APIView):
    def get(self, request):
        wMessage = "Hola" + request.user.username
        if request.user.is_authenticated:
            wMessage = "Hola " + request.user.username
        return render(request, 'index.html', {'wMessage': wMessage})

class UserRegisterView(APIView):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'registro.html', {'form': form})
    
    def post(request):
        form = UserRegisterForm(request, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-login')
        else:
            return render(request, 'registro.html', {'form': form})

class UserLoginView(APIView):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
            else:
                return render(request, 'login.html', {'form': form})
        else:
            return render(request, 'login.html', {'form': form})

class UserLogout(APIView):
    def get(self, request):
        logout(request)
        return redirect('homepage')
