from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class AuthTests(APITestCase):
    def test_signup(self):
        response = self.client.post('/signup/', {
            'username': 'testuser',
            'password': 'testpassword',
            'nickname': 'testnickname'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)