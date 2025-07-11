"""
Permissions personnalisées pour l'API SoftDesk
Gère l'autorisation d'accès aux ressources selon les rôles utilisateur
"""

from rest_framework import permissions


class IsContributor(permissions.BasePermission):
    """SECURITY: Permission - seuls les contributeurs du projet peuvent accéder"""

    def has_object_permission(self, request, view, obj):
        # Gérer les différents types d'objets
        if hasattr(obj, 'project'):
            # Pour les Issues : obj.project
            project = obj.project
        elif hasattr(obj, 'issue'):
            # Pour les Comments : obj.issue.project
            project = obj.issue.project
        else:
            # Pour les Projects : obj lui-même
            project = obj
        return project.contributors.filter(user=request.user).exists()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """SECURITY: Permission - seul l'auteur peut modifier, lecture pour les autres"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
