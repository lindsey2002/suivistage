import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expiré. Reconnectez-vous.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token invalide.')

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('Utilisateur introuvable.')

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'