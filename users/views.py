from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class SignUpView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname')
        
        if User.objects.filter(username=username).exists():
            return Response({
                "error": {"code": "USER_ALREADY_EXISTS", "message": "이미 가입된 사용자입니다."}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password)
        user.profile.nickname = nickname  # 추가 프로필 정보 저장
        user.save()
        
        return Response({"username": username, "nickname": nickname}, status=status.HTTP_201_CREATED)

# JWT Token 생성
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            return Response({
                "error": {"code": "INVALID_CREDENTIALS", "message": "아이디 또는 비밀번호가 올바르지 않습니다."}
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        return Response({"token": str(refresh.access_token)}, status=status.HTTP_200_OK)