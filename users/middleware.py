from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import jwt
from .models import User


class CSRFExemptAPIMiddleware:
    """
    Middleware para eximir CSRF en endpoints API
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Eximir CSRF para rutas /api/
        if request.path.startswith('/api/'):
            request._dont_enforce_csrf_checks = True
        
        response = self.get_response(request)
        return response


class JWTAuthenticationMiddleware:
    """
    Middleware para autenticar usuarios usando JWT desde cookies
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtener el token JWT de la cookie 'parla_session'
        token = request.COOKIES.get('parla_session')
        
        if token:
            try:
                # Decodificar el token
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                
                # Obtener el usuario
                user_id = payload.get('user_id')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.user = user
                    except User.DoesNotExist:
                        request.user = AnonymousUser()
                else:
                    request.user = AnonymousUser()
                    
            except jwt.ExpiredSignatureError:
                # Token expirado
                request.user = AnonymousUser()
            except jwt.InvalidTokenError:
                # Token inválido
                request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response
