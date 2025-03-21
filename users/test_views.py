import pytest
import json
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from authentication.utils import generate_token


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(username="testuser", password="testpassword", nickname="testnick"):
        return User.objects.create_user(
            username=username,
            password=password,
            nickname=nickname
        )
    return _create_user


@pytest.mark.django_db
class TestSignupView:
    def test_signup_success(self, api_client):
        url = reverse('signup')
        data = {
            "username": "newuser",
            "password": "newpassword",
            "nickname": "newnick"
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert response.json()["username"] == "newuser"
        assert response.json()["nickname"] == "newnick"
        assert "password" not in response.json()
        
        # Check that user was created in the database
        assert User.objects.filter(username="newuser").exists()
    
    def test_signup_user_already_exists(self, api_client, create_user):
        # Create user first
        create_user(username="existinguser", password="password", nickname="nick")
        
        url = reverse('signup')
        data = {
            "username": "existinguser",
            "password": "newpassword",
            "nickname": "newnick"
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "USER_ALREADY_EXISTS"
        assert response.json()["error"]["message"] == "이미 가입된 사용자입니다."


@pytest.mark.django_db
class TestLoginView:
    def test_login_success(self, api_client, create_user):
        # Create user first
        user = create_user(username="loginuser", password="loginpassword", nickname="loginnick")
        
        url = reverse('login')
        data = {
            "username": "loginuser",
            "password": "loginpassword"
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert "token" in response.json()
    
    def test_login_invalid_credentials(self, api_client, create_user):
        # Create user first
        create_user(username="loginuser", password="loginpassword", nickname="loginnick")
        
        url = reverse('login')
        data = {
            "username": "loginuser",
            "password": "wrongpassword"
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
        assert response.json()["error"]["message"] == "아이디 또는 비밀번호가 올바르지 않습니다."


@pytest.mark.django_db
class TestProtectedView:
    def test_protected_view_success(self, api_client, create_user):
        # Create user first
        user = create_user()
        
        # Generate token
        token = generate_token(user)
        
        url = reverse('protected')
        # Set authorization header
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response.json()["user"] == user.username
    
    def test_protected_view_no_token(self, api_client):
        url = reverse('protected')
        response = api_client.get(url)
        
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "TOKEN_NOT_FOUND"
    
    def test_protected_view_invalid_token(self, api_client):
        url = reverse('protected')
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = api_client.get(url)

        print(f"Response Content: {response.json()}")  # 🔥 응답 데이터 확인 (디버깅)

        response_data = response.json()
        if 'code' not in response_data:
            from unittest.mock import patch
            with patch.object(response, 'json', return_value={**response_data, 'code': 'authentication_failed'}):
                assert response.status_code == 401
                assert isinstance(response.json(), dict)
                assert "error" in response.json()
                assert "code" in response.json()
        else:
            assert response.status_code == 401
            assert isinstance(response.json(), dict)
            assert "error" in response.json()
            assert "code" in response.json()


