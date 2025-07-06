"""
Configuration des URLs pour l'API SoftDesk
Définit toutes les routes de l'API REST pour la gestion des projets et l'authentification JWT
Routes définies manuellement pour un contrôle total et une clarté maximale
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

# Configuration des URLs de l'application
urlpatterns = [
    # === ROUTES D'AUTHENTIFICATION JWT ===
    # Ces routes ne nécessitent pas d'authentification (AllowAny)

    # Inscription d'un nouvel utilisateur
    # POST /api/auth/register/ → Création compte + génération JWT tokens
    path('auth/register/', views.RegisterView.as_view(), name='register'),

    # Connexion utilisateur
    # POST /api/auth/login/ → Authentification + génération JWT tokens
    path('auth/login/', views.login_view, name='login'),

    # Renouvellement du token d'accès
    # POST /api/auth/refresh/ → Nouveau access token avec refresh token
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profil de l'utilisateur connecté
    # GET /api/auth/profile/ → Informations utilisateur (nécessite JWT)
    path('auth/profile/', views.user_profile, name='user_profile'),

    # === ROUTES PROJETS (CRUD) ===
    # Toutes ces routes nécessitent une authentification JWT (IsAuthenticated)

    # Liste et création des projets
    # GET /api/projects/ → Liste des projets (seuls ceux où l'utilisateur est contributeur)
    # POST /api/projects/ → Créer un nouveau projet (l'auteur devient contributeur automatiquement)
    path('projects/', views.ProjectViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='project_list'),

    # Détail, modification et suppression d'un projet spécifique
    # GET /api/projects/{id}/ → Détail d'un projet
    # PUT /api/projects/{id}/ → Modifier complètement un projet (auteur seulement)
    # PATCH /api/projects/{id}/ → Modifier partiellement un projet (auteur seulement)
    # DELETE /api/projects/{id}/ → Supprimer un projet (auteur seulement)
    path('projects/<int:pk>/', views.ProjectViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='project_detail'),

    # === ROUTES CONTRIBUTEURS ===
    # Gestion des contributeurs d'un projet (auteur seulement peut modifier)

    # Liste et ajout des contributeurs
    # GET /api/projects/{id}/contributors/ → Liste des contributeurs
    # POST /api/projects/{id}/contributors/ → Ajouter un contributeur (auteur uniquement)
    path('projects/<int:pk>/contributors/', views.ProjectViewSet.as_view({
        'get': 'contributors',
        'post': 'add_contributor'
    }), name='project_contributors'),

    # Retirer un contributeur d'un projet
    # DELETE /api/projects/{id}/contributors/{user_id}/ → Retirer un contributeur (auteur seulement)
    path('projects/<int:pk>/contributors/<int:user_id>/', views.ProjectViewSet.as_view({
        'delete': 'remove_contributor'
    }), name='project_remove_contributor'),
]
