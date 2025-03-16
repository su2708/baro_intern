import jwt
import datetime
from django.conf import settings
from django.utils import timezone
from users.models import User


def generate_token(user):
    """Generate JWT token for the user."""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': timezone.now() + settings.JWT_EXPIRATION_TIME,
        'iat': timezone.now()
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    return token


def verify_token(token):
    """Verify JWT token and return the user."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload['user_id'])
        return {'user': user}
    except jwt.ExpiredSignatureError:
        return {'error': {'code': 'TOKEN_EXPIRED', 'message': '토큰이 만료되었습니다.'}}
    except jwt.InvalidTokenError:
        return {'error': {'code': 'INVALID_TOKEN', 'message': '토큰이 유효하지 않습니다.'}}
    except User.DoesNotExist:
        return {'error': {'code': 'INVALID_TOKEN', 'message': '토큰이 유효하지 않습니다.'}}