from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models import Rapport, Livrable, Affectation, Evaluation
from ..serializers import (
    RapportSerializer, RapportWriteSerializer,
    LivrableSerializer, LivrableWriteSerializer,
    EvaluationSerializer, AffectationSerializer
)
from ..permissions import IsStagiaire


class MesRapportsView(APIView):
    permission_classes = [IsAuthenticated, IsStagiaire]

    @extend_schema(
        summary="Lister mes rapports hebdomadaires",
        tags=['Stagiaire'],
    )
    def get(self, request):
        rapports = (
            Rapport.objects
            .filter(stagiaire=request.user)
            .prefetch_related('livrables')
            .order_by('-date_soumission')
        )
        return Response({
            'message': 'Mes rapports.',
            'data': RapportSerializer(rapports, many=True).data
        })

    @extend_schema(
        summary="Soumettre un rapport hebdomadaire",
        request=RapportWriteSerializer,
        tags=['Stagiaire'],
        examples=[
            OpenApiExample(
                'Exemple rapport',
                value={
                    'semaine': 1,
                    'date_debut_sem': '2026-01-05',
                    'date_fin_sem': '2026-01-11',
                    'contenu': 'Cette semaine j\'ai travaillé sur la mise en place du projet.',
                }
            )
        ]
    )
    def post(self, request):
        affectation = Affectation.objects.filter(
            stagiaire=request.user
        ).first()
        if not affectation:
            return Response(
                {'message': 'Vous n\'avez pas de stage affecté.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RapportWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data

        if Rapport.objects.filter(
            stagiaire=request.user,
            stage=affectation.stage,
            semaine=data['semaine']
        ).exists():
            return Response(
                {'message': 'Vous avez déjà soumis un rapport pour cette semaine.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        rapport = Rapport.objects.create(
            stagiaire=request.user,
            stage=affectation.stage,
            semaine=data['semaine'],
            date_debut_sem=data['date_debut_sem'],
            date_fin_sem=data['date_fin_sem'],
            contenu=data['contenu'],
            statut='en_attente',
        )
        return Response(
            {
                'message': 'Rapport soumis avec succès.',
                'data': RapportSerializer(rapport).data
            },
            status=status.HTTP_201_CREATED,
        )


class RapportDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStagiaire]

    @extend_schema(
        summary="Détail d'un rapport",
        tags=['Stagiaire'],
    )
    def get(self, request, pk):
        try:
            rapport = Rapport.objects.prefetch_related('livrables').get(
                pk=pk, stagiaire=request.user
            )
        except Rapport.DoesNotExist:
            return Response(
                {'message': 'Rapport introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'message': 'Détail du rapport.',
            'data': RapportSerializer(rapport).data
        })

    @extend_schema(
        summary="Modifier un rapport en attente ou rejeté",
        request=RapportWriteSerializer,
        tags=['Stagiaire'],
        examples=[
            OpenApiExample(
                'Exemple modification',
                value={
                    'semaine': 1,
                    'date_debut_sem': '2026-01-05',
                    'date_fin_sem': '2026-01-11',
                    'contenu': 'Contenu corrigé après retour du tuteur.',
                }
            )
        ]
    )
    def put(self, request, pk):
        try:
            rapport = Rapport.objects.get(pk=pk, stagiaire=request.user)
        except Rapport.DoesNotExist:
            return Response(
                {'message': 'Rapport introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if rapport.statut not in ('en_attente', 'rejete'):
            return Response(
                {'message': 'Ce rapport ne peut plus être modifié.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RapportWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        rapport.contenu = data['contenu']
        rapport.date_debut_sem = data['date_debut_sem']
        rapport.date_fin_sem = data['date_fin_sem']
        rapport.statut = 'en_attente'
        rapport.save()
        return Response({
            'message': 'Rapport mis à jour.',
            'data': RapportSerializer(rapport).data
        })


class LivrableCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStagiaire]

    @extend_schema(
        summary="Ajouter un livrable à un rapport",
        request=LivrableWriteSerializer,
        tags=['Stagiaire'],
        examples=[
            OpenApiExample(
                'Exemple livrable lien',
                value={
                    'nom': 'Rapport PDF semaine 1',
                    'type': 'lien',
                    'url_ou_chemin': 'https://drive.google.com/mon-rapport',
                }
            )
        ]
    )
    def post(self, request, rapport_pk):
        try:
            rapport = Rapport.objects.get(pk=rapport_pk, stagiaire=request.user)
        except Rapport.DoesNotExist:
            return Response(
                {'message': 'Rapport introuvable.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if rapport.statut not in ('en_attente', 'rejete'):
            return Response(
                {'message': 'Impossible d\'ajouter un livrable à ce rapport.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LivrableWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Erreur de validation.', 'errors': serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        data = serializer.validated_data
        livrable = Livrable.objects.create(
            rapport=rapport,
            nom=data['nom'],
            type=data['type'],
            url_ou_chemin=data['url_ou_chemin'],
        )
        return Response(
            {
                'message': 'Livrable ajouté.',
                'data': LivrableSerializer(livrable).data
            },
            status=status.HTTP_201_CREATED,
        )


class MonEvaluationView(APIView):
    permission_classes = [IsAuthenticated, IsStagiaire]

    @extend_schema(
        summary="Consulter mon évaluation finale",
        tags=['Stagiaire'],
    )
    def get(self, request):
        affectation = Affectation.objects.filter(
            stagiaire=request.user
        ).first()
        if not affectation:
            return Response(
                {'message': 'Aucune affectation trouvée.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            evaluation = Evaluation.objects.get(affectation=affectation)
        except Evaluation.DoesNotExist:
            return Response(
                {'message': 'Aucune évaluation disponible pour le moment.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'message': 'Mon évaluation.',
            'data': EvaluationSerializer(evaluation).data
        })