from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
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

    @extend_schema(
        summary="Inscription d'un nouvel utilisateur",
        request=RegisterSerializer,
        tags=['Authentification'],
        examples=[
            OpenApiExample(
                'Exemple inscription',
                value={
                    'nom': 'Diallo',
                    'prenom': 'Mamadou',
                    'email': 'stagiaire@suivistage.com',
                    'mot_de_passe': 'password123',
                    'mot_de_passe_confirmation': 'password123',
                    'role': 'stagiaire'
                }
            )
        ]
    )
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

    @extend_schema(
        summary="Connexion et obtention du token JWT",
        request=LoginSerializer,
        tags=['Authentification'],
        examples=[
            OpenApiExample(
                'Exemple connexion',
                value={
                    'email': 'admin@suivistage.com',
                    'mot_de_passe': 'password123',
                }
            )
        ]
    )
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
        if not user.est_actif:
            return Response(
                {'message': 'Votre compte a été désactivé. Contactez l\'administrateur.'},
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

    @extend_schema(
        summary="Déconnexion",
        tags=['Authentification'],
    )
    def post(self, request):
        return Response({'message': 'Déconnexion réussie. Supprimez le token côté client.'})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Profil de l'utilisateur connecté",
        tags=['Authentification'],
    )
    def get(self, request):
        return Response({
            'message': 'Profil récupéré.',
            'user': UserPublicSerializer(request.user).data,
        })