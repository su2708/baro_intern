# users/utils.py 또는 적절한 위치에 추가
from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    # 인증 관련 예외 처리
    if response is not None and response.status_code == status.HTTP_401_UNAUTHORIZED:
        response.data = {
            'error': 'INVALID_TOKEN',
            'code': 'authentication_failed'
        }
    
    return response