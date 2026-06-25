from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('stagiaire', 'Stagiaire'),
        ('tuteur', 'Tuteur'),
        ('administrateur', 'Administrateur'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    mot_de_passe = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    is_authenticated = True
    is_anonymous = False

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.role})"


class Stage(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    entreprise = models.CharField(max_length=150)
    date_debut = models.DateField()
    date_fin = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stages'

    def __str__(self):
        return self.titre


class Affectation(models.Model):
    stagiaire = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='affectations_stagiaire'
    )
    tuteur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='affectations_tuteur'
    )
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, related_name='affectations'
    )
    date_affectation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'affectations'

    def __str__(self):
        return f"{self.stagiaire} → {self.tuteur} ({self.stage})"


class Rapport(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('rejete', 'Rejeté'),
        ('archive', 'Archivé'),
    ]

    stagiaire = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rapports'
    )
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, related_name='rapports'
    )
    semaine = models.IntegerField()
    date_debut_sem = models.DateField()
    date_fin_sem = models.DateField()
    contenu = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    commentaire_tuteur = models.TextField(blank=True, null=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'rapports'
        unique_together = ('stagiaire', 'stage', 'semaine')

    def __str__(self):
        return f"Rapport S{self.semaine} - {self.stagiaire}"


class Livrable(models.Model):
    TYPE_CHOICES = [
        ('fichier', 'Fichier'),
        ('lien', 'Lien'),
    ]

    rapport = models.ForeignKey(
        Rapport, on_delete=models.CASCADE, related_name='livrables'
    )
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    url_ou_chemin = models.CharField(max_length=500)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'livrables'

    def __str__(self):
        return self.nom


class Evaluation(models.Model):
    affectation = models.OneToOneField(
        Affectation, on_delete=models.CASCADE, related_name='evaluation'
    )
    note = models.DecimalField(max_digits=4, decimal_places=2)
    appreciation = models.TextField()
    points_forts = models.TextField(blank=True, null=True)
    points_ameliorer = models.TextField(blank=True, null=True)
    date_redaction = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evaluations'

    def __str__(self):
        return f"Évaluation {self.affectation} - {self.note}/20"