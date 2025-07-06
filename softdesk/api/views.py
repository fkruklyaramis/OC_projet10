from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Project, Contributor, Issue, Comment
from .serializers import (
    UserSerializer, LoginSerializer, ProjectSerializer,
    ContributorSerializer, ContributorCreateSerializer,
    IssueSerializer, IssueCreateSerializer, IssueUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    Inscription d'un nouvel utilisateur avec génération automatique de tokens JWT
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Inscription d'un nouvel utilisateur",
        operation_description="""
        Crée un compte utilisateur et retourne automatiquement les tokens JWT.
        L'utilisateur doit avoir au moins 15 ans (contrôle par date de naissance).
        """,
        responses={
            201: openapi.Response(
                description="Utilisateur créé avec succès",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "alice",
                            "email": "alice@example.com",
                            "first_name": "Alice",
                            "last_name": "Dupont"
                        },
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                    }
                }
            ),
            400: "Données invalides (âge < 15 ans, email déjà utilisé, etc.)"
        },
        tags=['Authentication']
    )
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


@swagger_auto_schema(
    method='post',
    operation_summary="Connexion utilisateur",
    operation_description="Authentifie un utilisateur et retourne les tokens JWT",
    request_body=LoginSerializer,
    responses={
        200: openapi.Response(
            description="Connexion réussie",
            examples={
                "application/json": {
                    "user": {
                        "id": 1,
                        "username": "alice",
                        "email": "alice@example.com"
                    },
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
                }
            }
        ),
        400: "Identifiants invalides"
    },
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Connexion utilisateur avec génération de tokens JWT
    """
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


@swagger_auto_schema(
    method='get',
    operation_summary="Profil utilisateur connecté",
    operation_description="Retourne les informations de l'utilisateur authentifié",
    responses={
        200: UserSerializer,
        401: "Token manquant ou invalide"
    },
    tags=['Authentication']
)
@api_view(['GET'])
def user_profile(request):
    """
    Profil de l'utilisateur connecté
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée : seul l'auteur peut modifier/supprimer
    """
    def has_object_permission(self, request, view, obj):
        # Lecture pour tous les contributeurs
        if request.method in permissions.SAFE_METHODS:
            return True
        # Écriture seulement pour l'auteur
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    """
    Permission personnalisée : seuls les contributeurs peuvent accéder
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            return True  # Pour créer un projet
        return True

    def has_object_permission(self, request, view, obj):
        # Vérifier si l'utilisateur est contributeur du projet
        if hasattr(obj, 'project'):  # Pour Issue et Comment
            project = obj.project
        else:  # Pour Project
            project = obj

        return project.contributors.filter(user=request.user).exists()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion complète des projets collaboratifs
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor, IsAuthorOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Liste des projets",
        operation_description="Retourne la liste des projets où l'utilisateur est contributeur",
        responses={200: ProjectSerializer(many=True)},
        tags=['Projects']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Créer un projet",
        operation_description="""
        Crée un nouveau projet. L'utilisateur devient automatiquement
        auteur et contributeur du projet.
        """,
        responses={
            201: ProjectSerializer,
            400: "Données invalides"
        },
        tags=['Projects']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Détail d'un projet",
        operation_description="Affiche les détails d'un projet (contributeurs uniquement)",
        responses={
            200: ProjectSerializer,
            403: "Accès refusé (non-contributeur)",
            404: "Projet non trouvé"
        },
        tags=['Projects']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Modifier un projet",
        operation_description="Modifie un projet (auteur uniquement)",
        responses={
            200: ProjectSerializer,
            403: "Accès refusé (non-auteur)",
            404: "Projet non trouvé"
        },
        tags=['Projects']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Supprimer un projet",
        operation_description="Supprime définitivement un projet (auteur uniquement)",
        responses={
            204: "Projet supprimé",
            403: "Accès refusé (non-auteur)",
            404: "Projet non trouvé"
        },
        tags=['Projects']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        # Un utilisateur ne voit que les projets où il est contributeur
        return Project.objects.filter(contributors__user=self.request.user).distinct()

    @swagger_auto_schema(
        operation_summary="Liste des contributeurs",
        operation_description="Affiche tous les contributeurs d'un projet",
        responses={200: ContributorSerializer(many=True)},
        tags=['Contributors']
    )
    def contributors(self, request, pk=None):
        """
        Liste des contributeurs d'un projet
        Route : GET /api/projects/{pk}/contributors/
        """
        project = self.get_object()
        contributors = project.contributors.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Ajouter un contributeur",
        operation_description="Ajoute un utilisateur comme contributeur (auteur uniquement)",
        request_body=ContributorCreateSerializer,
        responses={
            201: ContributorSerializer,
            400: "Utilisateur inexistant ou déjà contributeur",
            403: "Accès refusé (non-auteur)"
        },
        tags=['Contributors']
    )
    def add_contributor(self, request, pk=None):
        """
        Ajouter un contributeur à un projet (seul l'auteur peut le faire)
        """
        project = self.get_object()

        # Vérifier que seul l'auteur peut ajouter des contributeurs
        if project.author != request.user:
            return Response(
                {"error": "Seul l'auteur peut ajouter des contributeurs"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Passer le projet dans le contexte du serializer
        serializer = ContributorCreateSerializer(
            data=request.data,
            context={'project': project}
        )

        if serializer.is_valid():
            contributor = serializer.save()
            # Retourner les données du contributeur créé
            return Response(
                ContributorSerializer(contributor).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Retirer un contributeur",
        operation_description="Retire un contributeur du projet (auteur uniquement)",
        responses={
            204: "Contributeur retiré",
            400: "Impossible de retirer l'auteur",
            403: "Accès refusé (non-auteur)",
            404: "Contributeur non trouvé"
        },
        tags=['Contributors']
    )
    def remove_contributor(self, request, pk=None, user_id=None):
        """
        Retirer un contributeur d'un projet (seul l'auteur peut le faire)
        Utilise user_id depuis l'URL : /api/projects/{pk}/contributors/{user_id}/
        """
        project = self.get_object()

        # Vérifier que seul l'auteur peut retirer des contributeurs
        if project.author != request.user:
            return Response(
                {"error": "Seul l'auteur peut retirer des contributeurs"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            contributor = project.contributors.get(user_id=user_id)
            # Empêcher la suppression de l'auteur
            if contributor.user == project.author:
                return Response(
                    {"error": "L'auteur ne peut pas être retiré du projet"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            contributor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contributor.DoesNotExist:
            return Response(
                {"error": "Contributeur non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des issues/tâches d'un projet
    """
    permission_classes = [permissions.IsAuthenticated, IsContributor]

    def get_serializer_class(self):
        """
        Retourne le bon serializer selon l'action
        """
        if self.action == 'create':
            return IssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IssueUpdateSerializer
        return IssueSerializer

    def get_queryset(self):
        """
        Filtrer les issues par projet et s'assurer que l'utilisateur est contributeur
        """
        project_id = self.kwargs.get('project_pk')
        try:
            project = Project.objects.get(pk=project_id)
            # Vérifier que l'utilisateur est contributeur
            if not project.contributors.filter(user=self.request.user).exists():
                return Issue.objects.none()
            return project.issues.all()
        except Project.DoesNotExist:
            return Issue.objects.none()

    def get_project(self):
        """
        Récupère le projet depuis l'URL et vérifie les permissions
        """
        project_id = self.kwargs.get('project_pk')
        try:
            project = Project.objects.get(pk=project_id)
            # Vérifier que l'utilisateur est contributeur
            if not project.contributors.filter(user=self.request.user).exists():
                raise PermissionError("Vous n'êtes pas contributeur de ce projet.")
            return project
        except Project.DoesNotExist:
            raise Project.DoesNotExist("Le projet n'existe pas.")

    def get_serializer_context(self):
        """
        Ajoute le projet au contexte du serializer
        """
        context = super().get_serializer_context()
        try:
            context['project'] = self.get_project()
        except (Project.DoesNotExist, PermissionError):
            pass
        return context

    @swagger_auto_schema(
        operation_summary="Liste des issues d'un projet",
        operation_description="Retourne toutes les issues d'un projet (contributeurs uniquement)",
        responses={200: IssueSerializer(many=True)},
        tags=['Issues']
    )
    def list(self, request, *args, **kwargs):
        """
        Liste des issues d'un projet
        Route : GET /api/projects/{project_id}/issues/
        """
        try:
            project = self.get_project()
            issues = self.get_queryset()
            serializer = self.get_serializer(issues, many=True)
            return Response({
                'project': project.name,
                'issues_count': issues.count(),
                'issues': serializer.data
            })
        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Créer une issue",
        operation_description="""
        Crée une nouvelle issue dans un projet.
        L'assigné doit être un contributeur du projet.
        """,
        request_body=IssueCreateSerializer,
        responses={
            201: IssueSerializer,
            400: "Données invalides ou assigné non-contributeur",
            403: "Accès refusé (non-contributeur)"
        },
        tags=['Issues']
    )
    def create(self, request, *args, **kwargs):
        """
        Créer une nouvelle issue
        Route : POST /api/projects/{project_id}/issues/
        """
        try:
            self.get_project()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                issue = serializer.save()
                # Retourner l'issue créée avec le serializer complet
                return Response(
                    IssueSerializer(issue).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Détail d'une issue",
        operation_description="Affiche les détails d'une issue spécifique",
        responses={
            200: IssueSerializer,
            403: "Accès refusé (non-contributeur)",
            404: "Issue non trouvée"
        },
        tags=['Issues']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Détail d'une issue spécifique
        Route : GET /api/projects/{project_id}/issues/{issue_id}/
        """
        try:
            self.get_project()
            issue = self.get_object()
            serializer = self.get_serializer(issue)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Modifier une issue",
        operation_description="Modifie une issue (auteur de l'issue ou du projet)",
        request_body=IssueUpdateSerializer,
        responses={
            200: IssueSerializer,
            403: "Accès refusé",
            404: "Issue non trouvée"
        },
        tags=['Issues']
    )
    def update(self, request, *args, **kwargs):
        """
        Modifier une issue (PUT/PATCH)
        Route : PUT/PATCH /api/projects/{project_id}/issues/{issue_id}/
        """
        try:
            project = self.get_project()
            issue = self.get_object()

            # Seul l'auteur de l'issue peut la modifier (ou l'auteur du projet)
            if issue.author != request.user and project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur de l'issue ou du projet peut la modifier"},
                    status=status.HTTP_403_FORBIDDEN
                )

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(issue, data=request.data, partial=partial)

            if serializer.is_valid():
                serializer.save()
                return Response(IssueSerializer(issue).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Supprimer une issue",
        operation_description="Supprime définitivement une issue (auteur de l'issue ou du projet)",
        responses={
            204: "Issue supprimée",
            403: "Accès refusé",
            404: "Issue non trouvée"
        },
        tags=['Issues']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Supprimer une issue
        Route : DELETE /api/projects/{project_id}/issues/{issue_id}/
        """
        try:
            project = self.get_project()
            issue = self.get_object()

            # Seul l'auteur de l'issue peut la supprimer (ou l'auteur du projet)
            if issue.author != request.user and project.author != request.user:
                return Response(
                    {"error": "Seul l'auteur de l'issue ou du projet peut la supprimer"},
                    status=status.HTTP_403_FORBIDDEN
                )

            issue.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commentaires d'une issue
    - Seuls les contributeurs du projet peuvent accéder aux commentaires
    - Seul l'auteur du commentaire peut le modifier/supprimer
    """
    permission_classes = [permissions.IsAuthenticated, IsContributor]

    def get_serializer_class(self):
        """
        Retourne le bon serializer selon l'action
        """
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CommentUpdateSerializer
        return CommentSerializer

    def get_object(self):
        """
        Récupère un commentaire spécifique par son UUID
        en vérifiant qu'il appartient bien au projet et à l'issue spécifiés
        """
        project_id = self.kwargs.get('project_pk')
        issue_id = self.kwargs.get('issue_pk')
        comment_id = self.kwargs.get('pk')

        try:
            # Vérifier que le projet existe et que l'utilisateur est contributeur
            project = Project.objects.get(pk=project_id)
            if not project.contributors.filter(user=self.request.user).exists():
                raise PermissionError("Vous n'êtes pas contributeur de ce projet.")

            # Vérifier que l'issue existe dans ce projet
            issue = Issue.objects.get(pk=issue_id, project=project)

            # Récupérer le commentaire par UUID dans cette issue
            comment = Comment.objects.get(pk=comment_id, issue=issue)

            return comment

        except Project.DoesNotExist:
            raise Project.DoesNotExist("Le projet n'existe pas.")
        except Issue.DoesNotExist:
            raise Issue.DoesNotExist("L'issue n'existe pas.")
        except Comment.DoesNotExist:
            raise Comment.DoesNotExist("Le commentaire n'existe pas.")

    def get_queryset(self):
        """
        Filtrer les commentaires par issue et s'assurer que l'utilisateur est contributeur
        """
        project_id = self.kwargs.get('project_pk')
        issue_id = self.kwargs.get('issue_pk')

        try:
            project = Project.objects.get(pk=project_id)
            issue = Issue.objects.get(pk=issue_id, project=project)

            # Vérifier que l'utilisateur est contributeur
            if not project.contributors.filter(user=self.request.user).exists():
                return Comment.objects.none()

            return issue.comments.all()
        except (Project.DoesNotExist, Issue.DoesNotExist):
            return Comment.objects.none()

    def get_issue(self):
        """
        Récupère l'issue depuis l'URL et vérifie les permissions
        """
        project_id = self.kwargs.get('project_pk')
        issue_id = self.kwargs.get('issue_pk')

        try:
            project = Project.objects.get(pk=project_id)
            issue = Issue.objects.get(pk=issue_id, project=project)

            # Vérifier que l'utilisateur est contributeur
            if not project.contributors.filter(user=self.request.user).exists():
                raise PermissionError("Vous n'êtes pas contributeur de ce projet.")

            return issue
        except Project.DoesNotExist:
            raise Project.DoesNotExist("Le projet n'existe pas.")
        except Issue.DoesNotExist:
            raise Issue.DoesNotExist("L'issue n'existe pas.")

    def get_serializer_context(self):
        """
        Ajoute l'issue au contexte du serializer
        """
        context = super().get_serializer_context()
        try:
            context['issue'] = self.get_issue()
        except (Project.DoesNotExist, Issue.DoesNotExist, PermissionError):
            pass
        return context

    @swagger_auto_schema(
        operation_summary="Liste des commentaires",
        operation_description="Affiche tous les commentaires d'une issue",
        responses={200: CommentSerializer(many=True)},
        tags=['Comments']
    )
    def list(self, request, *args, **kwargs):
        """
        Liste des commentaires d'une issue
        Route : GET /api/projects/{project_id}/issues/{issue_id}/comments/
        """
        try:
            issue = self.get_issue()
            comments = self.get_queryset()
            serializer = self.get_serializer(comments, many=True)
            return Response({
                'project': issue.project.name,
                'issue': issue.name,
                'comments_count': comments.count(),
                'comments': serializer.data
            })
        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Créer un commentaire",
        operation_description="Ajoute un commentaire à une issue (contributeurs uniquement)",
        request_body=CommentCreateSerializer,
        responses={
            201: CommentSerializer,
            400: "Description requise",
            403: "Accès refusé (non-contributeur)"
        },
        tags=['Comments']
    )
    def create(self, request, *args, **kwargs):
        """
        Créer un nouveau commentaire
        Route : POST /api/projects/{project_id}/issues/{issue_id}/comments/
        """
        try:
            self.get_issue()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                comment = serializer.save()
                # Retourner le commentaire créé avec le serializer complet
                return Response(
                    CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Détail d'un commentaire",
        operation_description="Affiche les détails d'un commentaire spécifique",
        responses={
            200: CommentSerializer,
            403: "Accès refusé (non-contributeur)",
            404: "Commentaire non trouvé"
        },
        tags=['Comments']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Détail d'un commentaire spécifique
        Route : GET /api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
        """
        try:
            self.get_issue()
            comment = self.get_object()
            serializer = self.get_serializer(comment)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Modifier un commentaire",
        operation_description="Modifie un commentaire (auteur uniquement)",
        request_body=CommentUpdateSerializer,
        responses={
            200: CommentSerializer,
            403: "Accès refusé (non-auteur)",
            404: "Commentaire non trouvé"
        },
        tags=['Comments']
    )
    def update(self, request, *args, **kwargs):
        """
        Modifier un commentaire (PUT/PATCH)
        Route : PUT/PATCH /api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
        """
        try:
            self.get_issue()
            comment = self.get_object()

            # Seul l'auteur du commentaire peut le modifier
            if comment.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du commentaire peut le modifier"},
                    status=status.HTTP_403_FORBIDDEN
                )

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(comment, data=request.data, partial=partial)

            if serializer.is_valid():
                serializer.save()
                return Response(CommentSerializer(comment).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )

    @swagger_auto_schema(
        operation_summary="Supprimer un commentaire",
        operation_description="Supprime définitivement un commentaire (auteur uniquement)",
        responses={
            204: "Commentaire supprimé",
            403: "Accès refusé (non-auteur)",
            404: "Commentaire non trouvé"
        },
        tags=['Comments']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Supprimer un commentaire
        Route : DELETE /api/projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
        """
        try:
            self.get_issue()
            comment = self.get_object()

            # Seul l'auteur du commentaire peut le supprimer
            if comment.author != request.user:
                return Response(
                    {"error": "Seul l'auteur du commentaire peut le supprimer"},
                    status=status.HTTP_403_FORBIDDEN
                )

            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Project.DoesNotExist:
            return Response(
                {"error": "Projet non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Issue.DoesNotExist:
            return Response(
                {"error": "Issue non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
