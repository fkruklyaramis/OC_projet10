from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Project, Contributor, Issue
from .serializers import (
    UserSerializer, LoginSerializer, ProjectSerializer,
    ContributorSerializer, ContributorCreateSerializer,
    IssueSerializer, IssueCreateSerializer, IssueUpdateSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    Inscription d'un nouvel utilisateur
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

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
    ViewSet pour la gestion des projets
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsContributor, IsAuthorOrReadOnly]

    def get_queryset(self):
        # Un utilisateur ne voit que les projets où il est contributeur
        return Project.objects.filter(contributors__user=self.request.user).distinct()

    def contributors(self, request, pk=None):
        """
        Liste des contributeurs d'un projet
        Route : GET /api/projects/{pk}/contributors/
        """
        project = self.get_object()
        contributors = project.contributors.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

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
    ViewSet pour la gestion des Issues d'un projet
    - Seuls les contributeurs du projet peuvent accéder aux issues
    - L'auteur et les contributeurs peuvent modifier les issues
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
