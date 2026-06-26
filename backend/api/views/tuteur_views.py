from datetime import datetime, timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models import Rapport, Affectation, Evaluation
from ..serializers import (
    RapportSerializer, RapportValidationSerializer,
    EvaluationSerializer, EvaluationWriteSerializer,
    AffectationSerializer
)
from ..permissions import IsTuteur


class MesStagiairesView(APIView):
    permission_classes = [IsAuthenticated, IsTuteur]

    @extend_schema(
        summary="Lister mes stagiaires",
        tags=['Tuteur'],
    )
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

    @extend_schema(
        summary="Lister les rapports de mes stagiaires",
        tags=['Tuteur'],
    )
    def get(self, request):
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

    @extend_schema(
        summary="Valider ou rejeter un rapport",
        request=RapportValidationSerializer,
        tags=['Tuteur'],
        examples=[
            OpenApiExample(
                'Exemple validation',
                value={
                    'statut': 'valide',
                    'commentaire_tuteur': '',
                }
            ),
            OpenApiExample(
                'Exemple rejet',
                value={
                    'statut': 'rejete',
                    'commentaire_tuteur': 'Le contenu est insuffisant, merci de détailler les tâches effectuées.',
                }
            ),
        ]
    )
    def post(self, request, pk):
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

    @extend_schema(
        summary="Lister mes évaluations rédigées",
        tags=['Tuteur'],
    )
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

    @extend_schema(
        summary="Rédiger l'évaluation finale d'un stagiaire",
        request=EvaluationWriteSerializer,
        tags=['Tuteur'],
        examples=[
            OpenApiExample(
                'Exemple évaluation',
                value={
                    'note': 15.50,
                    'appreciation': 'Très bon stagiaire, sérieux et impliqué.',
                    'points_forts': 'Autonomie, qualité du code, respect des délais.',
                    'points_ameliorer': 'Améliorer la communication écrite.',
                }
            )
        ]
    )
    def post(self, request, stagiaire_id):
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