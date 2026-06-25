from rest_framework import serializers
from .models import User, Stage, Affectation, Rapport, Livrable, Evaluation


# ─── USER ────────────────────────────────────────────────────

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nom', 'prenom', 'email', 'role', 'est_actif', 'date_creation']


class RegisterSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=100)
    prenom = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    mot_de_passe = serializers.CharField(min_length=8, write_only=True)
    mot_de_passe_confirmation = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=['stagiaire', 'tuteur', 'administrateur'],
        default='stagiaire',
        required=False,
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value

    def validate(self, data):
        if data['mot_de_passe'] != data['mot_de_passe_confirmation']:
            raise serializers.ValidationError({
                'mot_de_passe_confirmation': 'Les mots de passe ne correspondent pas.'
            })
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    mot_de_passe = serializers.CharField(write_only=True)


# ─── STAGE ───────────────────────────────────────────────────

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'


class StageWriteSerializer(serializers.Serializer):
    titre = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    entreprise = serializers.CharField(max_length=150)
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()

    def validate(self, data):
        if data['date_fin'] <= data['date_debut']:
            raise serializers.ValidationError({
                'date_fin': 'La date de fin doit être après la date de début.'
            })
        return data


# ─── AFFECTATION ─────────────────────────────────────────────

class AffectationSerializer(serializers.ModelSerializer):
    stagiaire = UserPublicSerializer(read_only=True)
    tuteur = UserPublicSerializer(read_only=True)
    stage = StageSerializer(read_only=True)

    class Meta:
        model = Affectation
        fields = '__all__'


class AffectationWriteSerializer(serializers.Serializer):
    stagiaire_id = serializers.IntegerField()
    tuteur_id = serializers.IntegerField()
    stage_id = serializers.IntegerField()

    def validate_stagiaire_id(self, value):
        try:
            user = User.objects.get(pk=value)
            if user.role != 'stagiaire':
                raise serializers.ValidationError('Cet utilisateur n\'est pas un stagiaire.')
        except User.DoesNotExist:
            raise serializers.ValidationError('Stagiaire introuvable.')
        return value

    def validate_tuteur_id(self, value):
        try:
            user = User.objects.get(pk=value)
            if user.role != 'tuteur':
                raise serializers.ValidationError('Cet utilisateur n\'est pas un tuteur.')
        except User.DoesNotExist:
            raise serializers.ValidationError('Tuteur introuvable.')
        return value

    def validate_stage_id(self, value):
        if not Stage.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Stage introuvable.')
        return value


# ─── RAPPORT ─────────────────────────────────────────────────

class LivrableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livrable
        fields = '__all__'


class RapportSerializer(serializers.ModelSerializer):
    stagiaire = UserPublicSerializer(read_only=True)
    livrables = LivrableSerializer(many=True, read_only=True)

    class Meta:
        model = Rapport
        fields = '__all__'


class RapportWriteSerializer(serializers.Serializer):
    semaine = serializers.IntegerField(min_value=1)
    date_debut_sem = serializers.DateField()
    date_fin_sem = serializers.DateField()
    contenu = serializers.CharField()

    def validate(self, data):
        if data['date_fin_sem'] <= data['date_debut_sem']:
            raise serializers.ValidationError({
                'date_fin_sem': 'La date de fin doit être après la date de début.'
            })
        return data


class RapportValidationSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=['valide', 'rejete'])
    commentaire_tuteur = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['statut'] == 'rejete' and not data.get('commentaire_tuteur'):
            raise serializers.ValidationError({
                'commentaire_tuteur': 'Un commentaire est obligatoire en cas de rejet.'
            })
        return data


# ─── LIVRABLE ────────────────────────────────────────────────

class LivrableWriteSerializer(serializers.Serializer):
    nom = serializers.CharField(max_length=200)
    type = serializers.ChoiceField(choices=['fichier', 'lien'])
    url_ou_chemin = serializers.CharField(max_length=500)


# ─── EVALUATION ──────────────────────────────────────────────

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'


class EvaluationWriteSerializer(serializers.Serializer):
    note = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=0, max_value=20)
    appreciation = serializers.CharField()
    points_forts = serializers.CharField(required=False, allow_blank=True)
    points_ameliorer = serializers.CharField(required=False, allow_blank=True)