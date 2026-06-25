from django.urls import path
from .views.auth_views import (
    RegisterView, LoginView, LogoutView, MeView
)
from .views.stagiaire_views import (
    MesRapportsView, RapportDetailView,
    LivrableCreateView, MonEvaluationView
)
from .views.tuteur_views import (
    MesStagiairesView, RapportsASvaliderView,
    ValiderRapportView, MesEvaluationsView, CreerEvaluationView
)
from .views.admin_views import (
    AdminUserListView, AdminUserDetailView, AdminToggleUserView,
    AdminStageListCreateView, AdminStageDetailView,
    AdminAffectationListCreateView, AdminAffectationDetailView,
    AdminRapportListView, AdminEvaluationListView
)

urlpatterns = [

    # ─── AUTHENTIFICATION (publiques) ────────────────────────
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('me', MeView.as_view(), name='me'),

    # ─── STAGIAIRE ───────────────────────────────────────────
    path('stagiaire/rapports', MesRapportsView.as_view(), name='mes-rapports'),
    path('stagiaire/rapports/<int:pk>', RapportDetailView.as_view(), name='rapport-detail'),
    path('stagiaire/rapports/<int:rapport_pk>/livrables', LivrableCreateView.as_view(), name='livrable-create'),
    path('stagiaire/evaluation', MonEvaluationView.as_view(), name='mon-evaluation'),

    # ─── TUTEUR ──────────────────────────────────────────────
    path('tuteur/stagiaires', MesStagiairesView.as_view(), name='mes-stagiaires'),
    path('tuteur/rapports', RapportsASvaliderView.as_view(), name='rapports-a-valider'),
    path('tuteur/rapports/<int:pk>/valider', ValiderRapportView.as_view(), name='valider-rapport'),
    path('tuteur/evaluations', MesEvaluationsView.as_view(), name='mes-evaluations'),
    path('tuteur/stagiaires/<int:stagiaire_id>/evaluation', CreerEvaluationView.as_view(), name='creer-evaluation'),

    # ─── ADMIN - USERS ───────────────────────────────────────
    path('admin/users', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:pk>/toggle', AdminToggleUserView.as_view(), name='admin-toggle-user'),

    # ─── ADMIN - STAGES ──────────────────────────────────────
    path('admin/stages', AdminStageListCreateView.as_view(), name='admin-stages'),
    path('admin/stages/<int:pk>', AdminStageDetailView.as_view(), name='admin-stage-detail'),

    # ─── ADMIN - AFFECTATIONS ────────────────────────────────
    path('admin/affectations', AdminAffectationListCreateView.as_view(), name='admin-affectations'),
    path('admin/affectations/<int:pk>', AdminAffectationDetailView.as_view(), name='admin-affectation-detail'),

    # ─── ADMIN - RAPPORTS ────────────────────────────────────
    path('admin/rapports', AdminRapportListView.as_view(), name='admin-rapports'),

    # ─── ADMIN - EVALUATIONS ─────────────────────────────────
    path('admin/evaluations', AdminEvaluationListView.as_view(), name='admin-evaluations'),
]