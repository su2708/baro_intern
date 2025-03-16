from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer
from .models import User
from authentication.utils import generate_token
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SignupView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="회원가입 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description="회원가입 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'message': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            )
        }
    )
    def post(self, request):
        # Check if user already exists
        if User.objects.filter(username=request.data.get('username')).exists():
            return Response(
                {'error': {'code': 'USER_ALREADY_EXISTS', 'message': '이미 가입된 사용자입니다.'}},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'username': serializer.data['username'], 'nickname': serializer.data['nickname']},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="로그인 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: openapi.Response(
                description="로그인 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'message': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            )
        }
    )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                token = generate_token(user)
                return Response({'token': token}, status=status.HTTP_200_OK)
            
            return Response(
                {'error': {'code': 'INVALID_CREDENTIALS', 'message': '아이디 또는 비밀번호가 올바르지 않습니다.'}},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtectedView(APIView):
    """Test endpoint that requires authentication"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="토큰 인증이 필요한 예시 API",
        manual_parameters=[
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description="Bearer 토큰",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description="인증 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: openapi.Response(
                description="인증 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING),
                                'message': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {"error": {"code": "INVALID_TOKEN", "message": "유효하지 않은 토큰입니다."}},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({
            'message': '인증된 엔드포인트 접근 성공',
            'user': request.user.username
        }, status=status.HTTP_200_OK)
