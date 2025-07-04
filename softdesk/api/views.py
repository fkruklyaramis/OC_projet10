from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Project, Contributor
from .serializers import (
    UserSerializer, LoginSerializer, ProjectSerializer,
    ContributorSerializer, ContributorCreateSerializer
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

    @action(detail=True, methods=['get'])
    def contributors(self, request, pk=None):
        """
        Liste des contributeurs d'un projet
        """
        project = self.get_object()
        contributors = project.contributors.all()
        serializer = ContributorSerializer(contributors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
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

    @action(detail=True, methods=['delete'], url_path='remove_contributor/(?P<user_id>[^/.]+)')
    def remove_contributor(self, request, pk=None, user_id=None):
        """
        Retirer un contributeur d'un projet (seul l'auteur peut le faire)
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
