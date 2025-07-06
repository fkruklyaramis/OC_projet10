"""
Vues de l'API SoftDesk
Gère l'authentification, les projets, contributeurs, issues et commentaires
Documentation Swagger externalisée dans swagger_docs.py
"""

from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, LoginSerializer, ProjectSerializer,
    ContributorSerializer, ContributorCreateSerializer,
    IssueSerializer, IssueCreateSerializer, IssueUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer
)

# Import de la documentation Swagger
from .swagger_docs import (
    register_docs, login_docs, profile_docs,
    project_list_docs, project_create_docs, project_retrieve_docs,
    project_update_docs, project_partial_update_docs, project_destroy_docs,
    contributor_list_docs, contributor_add_docs, contributor_remove_docs,
    issue_list_docs, issue_create_docs, issue_retrieve_docs,
    issue_update_docs, issue_partial_update_docs, issue_destroy_docs,
    comment_list_docs, comment_create_docs, comment_retrieve_docs,
    comment_update_docs, comment_partial_update_docs, comment_destroy_docs,
    rgpd_export_docs, rgpd_delete_docs
)


# ================================
# PERMISSIONS PERSONNALISÉES
# ================================

class IsContributor(permissions.BasePermission):
    """SECURITY: Permission - seuls les contributeurs du projet peuvent accéder"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        return project.contributors.filter(user=request.user).exists()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """SECURITY: Permission - seul l'auteur peut modifier, lecture pour les autres"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


# ================================
# AUTHENTIFICATION
# ================================

class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur avec génération automatique de tokens JWT"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @register_docs
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Génération des tokens JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


@login_docs
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Connexion utilisateur avec génération de tokens JWT"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@profile_docs
@api_view(['GET'])
def user_profile(request):
    """Profil de l'utilisateur connecté"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ================================
# PROJETS
# ================================

class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion complète des projets collaboratifs"""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor, IsAuthorOrReadOnly]

    def get_queryset(self):
        """OPTIMISATION: Requêtes optimisées avec select_related et prefetch_related"""
        return Project.objects.filter(
            contributors__user=self.request.user
        ).select_related('author').prefetch_related(
            'contributors__user',
            'issues__author',
            'issues__assignee',
            'issues__comments__author'
        ).distinct()

    @project_list_docs
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @project_create_docs
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # L'utilisateur connecté devient l'auteur
        project = serializer.save(author=request.user)

        # Ajouter l'auteur comme contributeur
        Contributor.objects.create(project=project, user=request.user)

        return Response(
            ProjectSerializer(project).data,
            status=status.HTTP_201_CREATED
        )

    @project_retrieve_docs
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @project_update_docs
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @project_partial_update_docs
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @project_destroy_docs
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ================================
# CONTRIBUTEURS
# ================================

class ContributorViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des contributeurs d'un projet"""
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor]

    def get_queryset(self):
        """OPTIMISATION: Requêtes optimisées"""
        project_id = self.kwargs['project_pk']
        return Contributor.objects.filter(
            project_id=project_id
        ).select_related('user', 'project')

    def get_project(self):
        """Récupère le projet et vérifie les permissions"""
        project_id = self.kwargs['project_pk']
        project = get_object_or_404(Project, id=project_id)

        # SECURITY: Vérifier que l'utilisateur est contributeur
        if not project.contributors.filter(user=self.request.user).exists():
            raise PermissionError("Vous n'êtes pas contributeur de ce projet")

        return project

    @contributor_list_docs
    def list(self, request, *args, **kwargs):
        try:
            self.get_project()
            return super().list(request, *args, **kwargs)
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @contributor_add_docs
    def create(self, request, *args, **kwargs):
        try:
            project = self.get_project()

            # SECURITY: Seul l'auteur peut ajouter des contributeurs
            if project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du projet peut ajouter des contributeurs"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = ContributorCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(project=project)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @contributor_remove_docs
    def destroy(self, request, *args, **kwargs):
        try:
            project = self.get_project()

            # SECURITY: Seul l'auteur peut retirer des contributeurs
            if project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du projet peut retirer des contributeurs"},
                    status=status.HTTP_403_FORBIDDEN
                )

            contributor = self.get_object()

            # Empêcher la suppression de l'auteur
            if contributor.user == project.author:
                return Response(
                    {"error": "L'auteur du projet ne peut pas être retiré"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            contributor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


# ================================
# ISSUES
# ================================

class IssueViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des issues dans un projet"""
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor]

    def get_queryset(self):
        """OPTIMISATION: Requêtes optimisées"""
        project_id = self.kwargs['project_pk']
        return Issue.objects.filter(
            project_id=project_id
        ).select_related('author', 'assignee', 'project').prefetch_related('comments')

    def get_project(self):
        """Récupère le projet et vérifie les permissions"""
        project_id = self.kwargs['project_pk']
        project = get_object_or_404(Project, id=project_id)

        # SECURITY: Vérifier que l'utilisateur est contributeur
        if not project.contributors.filter(user=self.request.user).exists():
            raise PermissionError("Vous n'êtes pas contributeur de ce projet")

        return project

    @issue_list_docs
    def list(self, request, *args, **kwargs):
        try:
            self.get_project()
            return super().list(request, *args, **kwargs)
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @issue_create_docs
    def create(self, request, *args, **kwargs):
        try:
            project = self.get_project()
            serializer = IssueCreateSerializer(data=request.data)

            if serializer.is_valid():
                issue = serializer.save(project=project, author=request.user)
                return Response(
                    IssueSerializer(issue).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @issue_retrieve_docs
    def retrieve(self, request, *args, **kwargs):
        try:
            self.get_project()
            return super().retrieve(request, *args, **kwargs)
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @issue_update_docs
    def update(self, request, *args, **kwargs):
        try:
            project = self.get_project()
            issue = self.get_object()

            # SECURITY: Seul l'auteur de l'issue peut la modifier (ou l'auteur du projet)
            if issue.author != request.user and project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur de l'issue ou du projet peut la modifier"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = IssueUpdateSerializer(issue, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(IssueSerializer(issue).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @issue_partial_update_docs
    def partial_update(self, request, *args, **kwargs):
        try:
            project = self.get_project()
            issue = self.get_object()

            # SECURITY: Seul l'auteur de l'issue peut la modifier (ou l'auteur du projet)
            if issue.author != request.user and project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur de l'issue ou du projet peut la modifier"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = IssueUpdateSerializer(issue, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(IssueSerializer(issue).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @issue_destroy_docs
    def destroy(self, request, *args, **kwargs):
        try:
            project = self.get_project()
            issue = self.get_object()

            # SECURITY: Seul l'auteur de l'issue peut la supprimer (ou l'auteur du projet)
            if issue.author != request.user and project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur de l'issue ou du projet peut la supprimer"},
                    status=status.HTTP_403_FORBIDDEN
                )

            issue.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


# ================================
# COMMENTAIRES
# ================================

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des commentaires sur une issue"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor]

    def get_queryset(self):
        """OPTIMISATION: Requêtes optimisées"""
        issue_id = self.kwargs['issue_pk']
        return Comment.objects.filter(
            issue_id=issue_id
        ).select_related('author', 'issue__project')

    def get_issue(self):
        """Récupère l'issue et vérifie les permissions"""
        project_id = self.kwargs['project_pk']
        issue_id = self.kwargs['issue_pk']

        project = get_object_or_404(Project, id=project_id)
        issue = get_object_or_404(Issue, id=issue_id, project=project)

        # SECURITY: Vérifier que l'utilisateur est contributeur
        if not project.contributors.filter(user=self.request.user).exists():
            raise PermissionError("Vous n'êtes pas contributeur de ce projet")

        return issue

    @comment_list_docs
    def list(self, request, *args, **kwargs):
        try:
            self.get_issue()
            return super().list(request, *args, **kwargs)
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @comment_create_docs
    def create(self, request, *args, **kwargs):
        try:
            issue = self.get_issue()
            serializer = CommentCreateSerializer(data=request.data)

            if serializer.is_valid():
                comment = serializer.save(issue=issue, author=request.user)
                return Response(
                    CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @comment_retrieve_docs
    def retrieve(self, request, *args, **kwargs):
        try:
            self.get_issue()
            return super().retrieve(request, *args, **kwargs)
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @comment_update_docs
    def update(self, request, *args, **kwargs):
        try:
            self.get_issue()
            comment = self.get_object()

            # SECURITY: Seul l'auteur du commentaire peut le modifier
            if comment.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du commentaire peut le modifier"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = CommentUpdateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(CommentSerializer(comment).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @comment_partial_update_docs
    def partial_update(self, request, *args, **kwargs):
        try:
            self.get_issue()
            comment = self.get_object()

            # SECURITY: Seul l'auteur du commentaire peut le modifier
            if comment.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du commentaire peut le modifier"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(CommentSerializer(comment).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @comment_destroy_docs
    def destroy(self, request, *args, **kwargs):
        try:
            self.get_issue()
            comment = self.get_object()

            # SECURITY: Seul l'auteur du commentaire peut le supprimer
            if comment.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du commentaire peut le supprimer"},
                    status=status.HTTP_403_FORBIDDEN
                )

            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


# ================================
# RGPD - CONFORMITÉ
# ================================

class GDPRViewSet(viewsets.ViewSet):
    """RGPD: Endpoints pour la conformité RGPD"""
    permission_classes = [permissions.IsAuthenticated]

    @rgpd_export_docs
    @action(detail=False, methods=['get'])
    def export_my_data(self, request):
        """RGPD: Droit d'accès - Article 15"""
        user = request.user

        # Collecter toutes les données utilisateur
        data = {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'can_be_contacted': user.can_be_contacted,
                'can_data_be_shared': user.can_data_be_shared,
                'created_time': user.created_time.isoformat(),
            },
            'projects_authored': list(user.authored_projects.values('id', 'name', 'created_time')),
            'contributions': list(user.contributions.values('project__name', 'created_time')),
            'issues_authored': list(user.authored_issues.values('title', 'created_time', 'project__name')),
            'issues_assigned': list(user.assigned_issues.values('title', 'created_time', 'project__name')),
            'comments_authored': list(user.authored_comments.values('description', 'created_time', 'issue__title')),
            'export_date': timezone.now().isoformat(),
            'rgpd_notice': 'Données exportées conformément à l\'Article 15 du RGPD'
        }

        response = Response(data)
        response['Content-Disposition'] = (
            f'attachment; filename="donnees_personnelles_{user.username}_'
            f'{timezone.now().strftime("%Y%m%d")}.json"'
        )
        return response

    @rgpd_delete_docs
    @action(detail=False, methods=['delete'])
    def delete_my_account(self, request):
        """RGPD: Droit à l'oubli - Article 17"""
        user = request.user

        # RGPD: Anonymisation plutôt que suppression pour préserver l'intégrité des données
        try:
            # Anonymiser les commentaires (garder le contenu mais supprimer l'attribution)
            user.authored_comments.update(author=None)

            # Anonymiser les issues (garder le contenu mais supprimer l'attribution)
            user.authored_issues.update(author=None, assignee=None)

            # Gérer les projets créés par l'utilisateur
            for project in user.authored_projects.all():
                if project.contributors.count() == 1:
                    # Si l'utilisateur est le seul contributeur, supprimer le projet
                    project.delete()
                else:
                    # Sinon, anonymiser l'auteur
                    project.author = None
                    project.save()

            # Supprimer les contributions
            user.contributions.all().delete()

            # Supprimer définitivement l'utilisateur
            user.delete()

            return Response(
                {"message": "Compte supprimé conformément au RGPD Article 17"},
                status=status.HTTP_204_NO_CONTENT
            )

        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la suppression: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
