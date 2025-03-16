import jwt
import datetime
from django.conf import settings
from django.utils import timezone
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError, ExpiredTokenError, InvalidToken



# def generate_token(user):
#     """Generate JWT token for the user."""
#     payload = {
#         'user_id': user.id,
#         'username': user.username,
#         'exp': timezone.now() + settings.JWT_EXPIRATION_TIME,
#         'iat': timezone.now()
#     }
    
#     token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
#     return token

def generate_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def verify_token(token):
    try:
        decoded_token = AccessToken(token)  # 🔥 JWT 토큰 검증
        user_id = decoded_token["user_id"]
        user = User.objects.get(id=user_id)  # 🔥 User 객체로 변환
        return {"user": user}  # 🔥 User 객체 반환
    except ExpiredTokenError:
        return {"error": "TOKEN_EXPIRED"}  # 🔥 만료된 토큰 예외 처리
    except (InvalidToken, TokenError, User.DoesNotExist):
        return {"error": "INVALID_TOKEN"}  # 🔥 잘못된 토큰 또는 유효하지 않은 사용자 예외 처리