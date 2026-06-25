from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import Rapport, Affectation, Evaluation, User
from ..serializers import (
    RapportSerializer, RapportValidationSerializer,
    EvaluationSerializer, EvaluationWriteSerializer,
    AffectationSerializer, UserPublicSerializer
)
from ..permissions import IsTuteur


class MesStagiairesView(APIView):
    permission_classes = [IsAuthenticated, IsTuteur]

    def get(self, request):
        affectations = (
            Affectation.objects
            .filter(tuteur=request.user)
            .select_related('stagiaire', 'stage')
        )
        return Response({
            'message': 'Mes stagiaires.',
            'data': AffectationSerializer(affectations, many=True).data
        })


class RapportsASvaliderView(APIView):
    permission_classes = [IsAuthenticated, IsTuteur]

    def get(self, request):
        # Récupérer les stagiaires du tuteur connecté
        stagiaire_ids = Affectation.objects.filter(
            tuteur=request.user
        ).values_list('stagiaire_id', flat=True)

        rapports = (
            Rapport.objects
            .filter(stagiaire_id__in=stagiaire_ids)
            .select_related('stagiaire', 'stage')
            .prefetch_related('livrables')
            .order_by('-date_soumission')
        )
        return Response({
            'message': 'Rapports de mes stagiaires.',
            'data': RapportSerializer(rapports, many=True).data
        })


class ValiderRapportView(APIView):
    permission_classes = [IsAuthenticated, IsTuteur]

    def post(self, request, pk):
        # Vérifier que le rapport appartient à un stagiaire du tuteur
        stagiaire_ids = Affectation.objects.filter(
            tuteur=request.user
        ).values_list('stagiaire_id', flat=True)

        try:
            rapport = Rapport.objects.get(pk=pk, stagiaire_id__in=stagiaire_ids)
        except Rapport.DoesNotExist:
            return Response(
                {'message': 'Rapport introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Règle métier : seulement les rapports en_attente peuvent être traités
        if rapport.statut != 'en_attente':
            return Response(
                {'message': 'Ce rapport a déjà été traité.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RapportValidationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        rapport.statut = data['statut']
        rapport.commentaire_tuteur = data.get('commentaire_tuteur', '')
        rapport.date_validation = datetime.now(tz=timezone.utc)
        rapport.save()

        return Response({
            'message': f"Rapport {data['statut']}.",
            'data': RapportSerializer(rapport).data
        })


class MesEvaluationsView(APIView):
    permission_classes = [IsAuthenticated, IsTuteur]

    def get(self, request):
        affectations = Affectation.objects.filter(
            tuteur=request.user
        ).values_list('id', flat=True)

        evaluations = (
            Evaluation.objects
            .filter(affectation_id__in=affectations)
            .select_related('affectation__stagiaire', 'affectation__stage')
        )
        return Response({
            'message': 'Mes évaluations.',
            'data': EvaluationSerializer(evaluations, many=True).data
        })


class CreerEvaluationView(APIView):
    permission_classes = [IsAuthenticated, IsTuteur]

    def post(self, request, stagiaire_id):
        # Vérifier que le stagiaire appartient bien au tuteur connecté
        try:
            affectation = Affectation.objects.get(
                tuteur=request.user,
                stagiaire_id=stagiaire_id
            )
        except Affectation.DoesNotExist:
            return Response(
                {'message': 'Ce stagiaire ne vous est pas affecté.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Règle métier : une seule évaluation par stage
        if Evaluation.objects.filter(affectation=affectation).exists():
            return Response(
                {'message': 'Une évaluation existe déjà pour ce stagiaire.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EvaluationWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        evaluation = Evaluation.objects.create(
            affectation=affectation,
            note=data['note'],
            appreciation=data['appreciation'],
            points_forts=data.get('points_forts', ''),
            points_ameliorer=data.get('points_ameliorer', ''),
        )
        return Response(
            {
                'message': 'Évaluation créée avec succès.',
                'data': EvaluationSerializer(evaluation).data
            },
            status=status.HTTP_201_CREATED,
        )