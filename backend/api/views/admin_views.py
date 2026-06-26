from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models import User, Stage, Affectation, Rapport, Evaluation
from ..serializers import (
    UserPublicSerializer,
    StageSerializer, StageWriteSerializer,
    AffectationSerializer, AffectationWriteSerializer,
    RapportSerializer, EvaluationSerializer
)
from ..permissions import IsAdministrateur


# ─── USERS ───────────────────────────────────────────────────

class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Lister tous les utilisateurs",
        tags=['Admin - Users'],
    )
    def get(self, request):
        users = User.objects.all().order_by('role', 'nom')
        return Response({
            'message': 'Liste des utilisateurs.',
            'data': UserPublicSerializer(users, many=True).data
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Détail d'un utilisateur",
        tags=['Admin - Users'],
    )
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'message': 'Utilisateur introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'message': 'Détail utilisateur.',
            'data': UserPublicSerializer(user).data
        })

    @extend_schema(
        summary="Supprimer un utilisateur",
        tags=['Admin - Users'],
    )
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'message': 'Utilisateur introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user.id == request.user.id:
            return Response(
                {'message': 'Vous ne pouvez pas supprimer votre propre compte.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.delete()
        return Response({'message': 'Utilisateur supprimé.'})


class AdminToggleUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Activer ou désactiver un utilisateur",
        tags=['Admin - Users'],
    )
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'message': 'Utilisateur introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user.id == request.user.id:
            return Response(
                {'message': 'Vous ne pouvez pas désactiver votre propre compte.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.est_actif = not user.est_actif
        user.save()
        etat = 'activé' if user.est_actif else 'désactivé'
        return Response({
            'message': f'Utilisateur {etat}.',
            'data': UserPublicSerializer(user).data
        })


# ─── STAGES ──────────────────────────────────────────────────

class AdminStageListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Lister tous les stages",
        tags=['Admin - Stages'],
    )
    def get(self, request):
        stages = Stage.objects.all().order_by('-date_creation')
        return Response({
            'message': 'Liste des stages.',
            'data': StageSerializer(stages, many=True).data
        })

    @extend_schema(
        summary="Créer un stage",
        request=StageWriteSerializer,
        tags=['Admin - Stages'],
        examples=[
            OpenApiExample(
                'Exemple stage',
                value={
                    'titre': 'Stage développement web',
                    'description': 'Développement d\'une application web en Django.',
                    'entreprise': 'Tech Dakar SARL',
                    'date_debut': '2026-07-01',
                    'date_fin': '2026-09-30',
                }
            )
        ]
    )
    def post(self, request):
        serializer = StageWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        stage = Stage.objects.create(
            titre=data['titre'],
            description=data.get('description', ''),
            entreprise=data['entreprise'],
            date_debut=data['date_debut'],
            date_fin=data['date_fin'],
        )
        return Response(
            {
                'message': 'Stage créé.',
                'data': StageSerializer(stage).data
            },
            status=status.HTTP_201_CREATED,
        )


class AdminStageDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Détail d'un stage",
        tags=['Admin - Stages'],
    )
    def get(self, request, pk):
        try:
            stage = Stage.objects.get(pk=pk)
        except Stage.DoesNotExist:
            return Response(
                {'message': 'Stage introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'message': 'Détail du stage.',
            'data': StageSerializer(stage).data
        })

    @extend_schema(
        summary="Modifier un stage",
        request=StageWriteSerializer,
        tags=['Admin - Stages'],
        examples=[
            OpenApiExample(
                'Exemple modification',
                value={
                    'titre': 'Stage développement web modifié',
                    'description': 'Description mise à jour.',
                    'entreprise': 'Tech Dakar SARL',
                    'date_debut': '2026-07-01',
                    'date_fin': '2026-10-31',
                }
            )
        ]
    )
    def put(self, request, pk):
        try:
            stage = Stage.objects.get(pk=pk)
        except Stage.DoesNotExist:
            return Response(
                {'message': 'Stage introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = StageWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        stage.titre = data['titre']
        stage.description = data.get('description', '')
        stage.entreprise = data['entreprise']
        stage.date_debut = data['date_debut']
        stage.date_fin = data['date_fin']
        stage.save()
        return Response({
            'message': 'Stage mis à jour.',
            'data': StageSerializer(stage).data
        })

    @extend_schema(
        summary="Supprimer un stage",
        tags=['Admin - Stages'],
    )
    def delete(self, request, pk):
        try:
            stage = Stage.objects.get(pk=pk)
        except Stage.DoesNotExist:
            return Response(
                {'message': 'Stage introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        stage.delete()
        return Response({'message': 'Stage supprimé.'})


# ─── AFFECTATIONS ────────────────────────────────────────────

class AdminAffectationListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Lister toutes les affectations",
        tags=['Admin - Affectations'],
    )
    def get(self, request):
        affectations = (
            Affectation.objects
            .all()
            .select_related('stagiaire', 'tuteur', 'stage')
            .order_by('-date_affectation')
        )
        return Response({
            'message': 'Liste des affectations.',
            'data': AffectationSerializer(affectations, many=True).data
        })

    @extend_schema(
        summary="Créer une affectation stagiaire-tuteur",
        request=AffectationWriteSerializer,
        tags=['Admin - Affectations'],
        examples=[
            OpenApiExample(
                'Exemple affectation',
                value={
                    'stagiaire_id': 2,
                    'tuteur_id': 3,
                    'stage_id': 1,
                }
            )
        ]
    )
    def post(self, request):
        serializer = AffectationWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        affectation = Affectation.objects.create(
            stagiaire_id=data['stagiaire_id'],
            tuteur_id=data['tuteur_id'],
            stage_id=data['stage_id'],
        )
        affectation_full = Affectation.objects.select_related(
            'stagiaire', 'tuteur', 'stage'
        ).get(pk=affectation.pk)
        return Response(
            {
                'message': 'Affectation créée.',
                'data': AffectationSerializer(affectation_full).data
            },
            status=status.HTTP_201_CREATED,
        )


class AdminAffectationDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Supprimer une affectation",
        tags=['Admin - Affectations'],
    )
    def delete(self, request, pk):
        try:
            affectation = Affectation.objects.get(pk=pk)
        except Affectation.DoesNotExist:
            return Response(
                {'message': 'Affectation introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        affectation.delete()
        return Response({'message': 'Affectation supprimée.'})


# ─── RAPPORTS ────────────────────────────────────────────────

class AdminRapportListView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Lister tous les rapports",
        tags=['Admin - Rapports'],
    )
    def get(self, request):
        rapports = (
            Rapport.objects
            .all()
            .select_related('stagiaire', 'stage')
            .prefetch_related('livrables')
            .order_by('-date_soumission')
        )
        return Response({
            'message': 'Tous les rapports.',
            'data': RapportSerializer(rapports, many=True).data
        })


# ─── EVALUATIONS ─────────────────────────────────────────────

class AdminEvaluationListView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrateur]

    @extend_schema(
        summary="Lister toutes les évaluations",
        tags=['Admin - Evaluations'],
    )
    def get(self, request):
        evaluations = (
            Evaluation.objects
            .all()
            .select_related('affectation__stagiaire', 'affectation__stage')
        )
        return Response({
            'message': 'Toutes les évaluations.',
            'data': EvaluationSerializer(evaluations, many=True).data
        })