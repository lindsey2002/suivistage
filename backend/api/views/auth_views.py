from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..models import User
from ..serializers import RegisterSerializer, LoginSerializer, UserPublicSerializer


def generate_token(user):
    payload = {
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(tz=timezone.utc) + timedelta(days=settings.JWT_EXPIRES_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        hashed = bcrypt.hashpw(data['mot_de_passe'].encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(
            nom=data['nom'],
            prenom=data['prenom'],
            email=data['email'],
            mot_de_passe=hashed,
            role=data.get('role', 'stagiaire'),
        )
        token = generate_token(user)
        return Response(
            {
                'message': 'Inscription réussie.',
                'user': UserPublicSerializer(user).data,
                'token': token,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            return Response(
                {'message': 'Identifiants incorrects.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not bcrypt.checkpw(data['mot_de_passe'].encode(), user.mot_de_passe.encode()):
            return Response(
                {'message': 'Identifiants incorrects.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token = generate_token(user)
        return Response({
            'message': 'Connexion réussie.',
            'user': UserPublicSerializer(user).data,
            'token': token,
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({'message': 'Déconnexion réussie. Supprimez le token côté client.'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Profil récupéré.',
            'user': UserPublicSerializer(request.user).data,
        })