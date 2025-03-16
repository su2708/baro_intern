from django.http import JsonResponse
from .utils import verify_token


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Endpoints that don't require authentication
        self.exempt_urls = ['/signup', '/login', '/swagger', '/swagger/', '/swagger(?P<format>\.json|\.yaml)', '/schema']
    
    def __call__(self, request):
        # Skip authentication for exempt URLs
        path = request.path_info.lstrip('/')
        
        if any(path.startswith(url.lstrip('/')) for url in self.exempt_urls):
            return self.get_response(request)
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return JsonResponse(
                {'error': {'code': 'TOKEN_NOT_FOUND', 'message': '토큰이 없습니다.'}},
                status=401
            )
        
        try:
            # Extract the token
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = auth_header
            
            # Verify token
            result = verify_token(token)
            
            if 'error' in result:
                return JsonResponse({'error': result['error']}, status=401)
            
            # Add user to request
            request.user = result['user']
            
            return self.get_response(request)
        
        except Exception:
            return JsonResponse(
                {'error': {'code': 'INVALID_TOKEN', 'message': '토큰이 유효하지 않습니다.'}},
                status=401
            )