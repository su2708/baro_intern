import pytest
import time
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from users.models import User
from authentication.utils import generate_token, verify_token


@pytest.fixture
def test_user():
    user = User.objects.create_user(
        username="testuser",
        password="testpassword",
        nickname="testnick"
    )
    return user


@pytest.mark.django_db
class TestJWTUtils:
    def test_generate_token(self, test_user):
        token = generate_token(test_user)
        assert isinstance(token, str)
    
    def test_verify_token_success(self, test_user):
        token = generate_token(test_user)
        result = verify_token(token)
        
        assert 'user' in result
        assert result['user'].id == test_user.id
    
    def test_verify_token_expired(self, test_user, settings):
        # Temporarily set JWT expiration to a very short time
        original_exp = settings.JWT_EXPIRATION_TIME
        settings.JWT_EXPIRATION_TIME = timedelta(milliseconds=1)
        
        token = generate_token(test_user)
        
        # Wait for token to expire
        time.sleep(0.01)
        
        result = verify_token(token)
        
        # Reset settings
        settings.JWT_EXPIRATION_TIME = original_exp
        
        assert 'error' in result
        assert result['error']['code'] == 'TOKEN_EXPIRED'
    
    def test_verify_token_invalid(self):
        result = verify_token("invalidt.oken.string")
        
        assert 'error' in result
        assert result['error']['code'] == 'INVALID_TOKEN'