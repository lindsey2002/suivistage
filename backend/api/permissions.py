from rest_framework.permissions import BasePermission


class IsAdministrateur(BasePermission):
    message = "Accès interdit. Rôle requis : administrateur."

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'administrateur')


class IsTuteur(BasePermission):
    message = "Accès interdit. Rôle requis : tuteur."

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'tuteur')


class IsStagiaire(BasePermission):
    message = "Accès interdit. Rôle requis : stagiaire."

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'stagiaire')


class IsTuteurOrAdministrateur(BasePermission):
    message = "Accès interdit. Rôle requis : tuteur ou administrateur."

    def has_permission(self, request, view):
        return bool(request.user and request.user.role in ('tuteur', 'administrateur'))