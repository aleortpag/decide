from django.test import TestCase, Client
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth import authenticate

from base import mods


class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_page_exists(self):
        response = self.client.get(reverse('user-login'))
        self.assertEqual(response.status_code, 200)

#    def test_login_successful(self):
#        url = reverse('user-login')
#        data = {'username': self.username, 'password': self.password}

#        response = self.client.post(url, data)
#        self.assertEqual(response.status_code, 302)
        
#        self.assertTrue(self.user.is_authenticated)

    def test_login_failure(self):
        url = reverse('user-login')
        data = {'username': 'incorrectuser', 'password': 'incorrectpassword'}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        user = authenticate(username='incorrectuser', password='incorrectpassword')
        self.assertIsNone(user)


class UserRegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('user-register')

    def test_register_page_exists(self):
        response = self.client.get(reverse('user-register'))
        self.assertEqual(response.status_code, 200)

    # def test_register_successful(self):
    #     valid_data = {
    #         'username': 'testuser',
    #         'email': 'test@example.com',
    #         'password1': 'testpassword123',
    #         'password2': 'testpassword123',
    #     }

#         # Hacer una solicitud POST con datos válidos
#         response = self.client.post(self.register_url, data=valid_data)

#         # Verificar que la respuesta redirige al login después de un registro exitoso
#         self.assertRedirects(response, reverse('user-login'))
#         # Verificar que se ha creado un usuario en la base de datos
#         self.assertTrue(User.objects.filter(username='testuser').exists())

    # def test_register_failure(self):
    #     invalid_data = {
    #         'username': 'testuser',
    #         'email': 'invalidemail',
    #         'password1': 'testpassword123',
    #         'password2': 'differentpassword',
    #     }

    #     response = self.client.post(self.register_url, data=invalid_data)

    #     # Verificar que la respuesta no redirige y vuelve a mostrar el formulario de registro
    #     self.assertEqual(response.status_code, 302)
    #     self.assertIn('form', response.context)
    #     # Verificar que el contenido de la respuesta contiene 'registro.html'
    #     self.assertContains(response, 'registro.html')
    #     # Verificar que no se ha creado un usuario en la base de datos
    #     self.assertFalse(User.objects.filter(username='testuser').exists())
