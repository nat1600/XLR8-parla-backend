from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.conf import settings
from .models import User
from .serializers import UserSerializer
import jwt
from datetime import datetime, timedelta
import requests as http_requests


class GoogleLoginView(APIView):
    """
    Endpoint para login con Google usando access token
    POST /api/users/google/login/
    Body: { "credential": "GOOGLE_ACCESS_TOKEN", "userInfo": {...} }
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            # Obtener el access token y la info del usuario
            access_token = request.data.get('credential')
            user_info = request.data.get('userInfo')
            
            if not access_token:
                return Response(
                    {'error': 'Token no proporcionado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Si no se proporciona userInfo, obtenerla de Google
            if not user_info:
                try:
                    google_response = http_requests.get(
                        'https://www.googleapis.com/oauth2/v3/userinfo',
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    
                    if google_response.status_code != 200:
                        return Response(
                            {'error': 'Token inválido o expirado'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                    
                    user_info = google_response.json()
                    
                except Exception as e:
                    return Response(
                        {'error': f'Error al verificar token con Google: {str(e)}'},
                        status=status.HTTP_401_UNAUTHORIZED
                    )
            
            # Extraer datos del usuario
            email = user_info.get('email')
            google_id = user_info.get('sub')
            name = user_info.get('name', '')
            picture = user_info.get('picture', '')
            
            if not email:
                return Response(
                    {'error': 'Email no encontrado en el token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar o crear usuario
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'google_id': google_id,
                    'profile_picture': picture,
                    'first_name': name.split()[0] if name else '',
                    'last_name': ' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                }
            )
            
            # Si el usuario ya existe, actualizar datos de Google
            if not created:
                if not user.google_id:
                    user.google_id = google_id
                if not user.profile_picture:
                    user.profile_picture = picture
                user.save()
            
            # Crear JWT token
            jwt_token = self.create_jwt_for_user(user)
            
            # Crear respuesta con cookie
            response = Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'profile_picture': user.profile_picture,
                },
                'message': 'Login exitoso' if not created else 'Usuario creado y autenticado'
            })
            
            # Setear cookie JWT
            response.set_cookie(
                key='parla_session',
                value=jwt_token,
                httponly=True,
                # En HTTPS permitimos SameSite=None para terceros (YouTube)
                secure=True,
                samesite='None',
                max_age=60*60*24*7,  # 1 semana
            )
            
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @staticmethod
    def create_jwt_for_user(user):
        """Crea un JWT token para el usuario"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token


class UserProfileView(APIView):
    """
    Endpoint para obtener el perfil del usuario autenticado
    GET /api/users/profile/
    Requiere: sesión válida (cookie de sesión o JWT)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Retorna los datos del usuario autenticado"""
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error al obtener perfil: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )