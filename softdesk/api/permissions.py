"""
Permissions personnalisées pour l'API SoftDesk

Ce module définit les permissions personnalisées pour contrôler l'accès
aux ressources selon les rôles et statuts des utilisateurs.
"""

from rest_framework import permissions


class IsContributor(permissions.BasePermission):
    """SECURITY: Permission - seuls les contributeurs du projet peuvent accéder"""

    def has_object_permission(self, request, view, obj):
        """
        Vérifie si l'utilisateur est contributeur du projet.

        Gère différents types d'objets (Project, Issue, Comment) pour retrouver
        le projet associé et vérifier l'appartenance de l'utilisateur.

        Args:
            request: La requête HTTP contenant l'utilisateur authentifié
            view: La vue Django REST Framework appelante
            obj: L'objet à vérifier (Project, Issue ou Comment)

        Returns:
            bool: True si l'utilisateur est contributeur du projet, False sinon
        """
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
        """
        Autorise la lecture pour tous les contributeurs.

        Pour les opérations de modification/suppression, seul l'auteur
        de l'objet est autorisé.

        Args:
            request: La requête HTTP avec la méthode (GET/POST/PUT/DELETE)
            view: La vue Django REST Framework appelante
            obj: L'objet à vérifier (Project, Issue ou Comment)

        Returns:
            bool: True si l'opération est autorisée, False sinon

        Note:
            - Méthodes SAFE (GET, HEAD, OPTIONS) : autorisées pour tous
            - Méthodes unsafe (POST, PUT, DELETE) : seulement pour l'auteur
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
