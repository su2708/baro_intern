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
        assert isinstance(result['user'], User)  # 🔥 User 객체인지 확인
        assert result['user'].id == test_user.id  # 🔥 User 객체의 id 비교
    
    def test_verify_token_expired(self, test_user, settings):
        # JWT 만료 시간을 임시로 1초로 설정
        original_exp = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(seconds=1)

        token = generate_token(test_user)

        # 토큰이 만료되도록 2초 대기
        time.sleep(2)

        result = verify_token(token)

        # 원래 설정 복원
        settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = original_exp

        assert "error" in result  # 🔥 에러가 반환되어야 함
        assert result["error"] == "TOKEN_EXPIRED"
    
    def test_verify_token_invalid(self):
        result = verify_token("invalidt.oken.string")  # 🔥 잘못된 토큰

        assert "error" in result  # 🔥 오류 메시지가 반환되어야 함
        assert result["error"] == "INVALID_TOKEN"
