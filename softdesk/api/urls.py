"""
URLs de l'API SoftDesk - Routes manuelles sans router
Organisation claire des endpoints avec gestion explicite des méthodes HTTP
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [

    # ================================
    # AUTHENTIFICATION
    # ================================

    path('auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('auth/login/', views.login_view, name='auth-login'),
    path('auth/profile/', views.user_profile, name='auth-profile'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),


    # ================================
    # PROJETS
    # ================================

    # Liste et création des projets
    path('projects/', views.ProjectViewSet.as_view({
        'get': 'list',           # GET /projects/ - Liste des projets
        'post': 'create'         # POST /projects/ - Créer un projet
    }), name='projects-list'),

    # Détail, modification et suppression d'un projet
    path('projects/<int:pk>/', views.ProjectViewSet.as_view({
        'get': 'retrieve',       # GET /projects/{id}/ - Détail du projet
        'put': 'update',         # PUT /projects/{id}/ - Modifier complètement
        'patch': 'partial_update',  # PATCH /projects/{id}/ - Modifier partiellement
        'delete': 'destroy'      # DELETE /projects/{id}/ - Supprimer
    }), name='projects-detail'),


    # ================================
    # CONTRIBUTEURS
    # ================================

    # Liste et ajout des contributeurs d'un projet
    path('projects/<int:project_pk>/contributors/', views.ContributorViewSet.as_view({
        'get': 'list',           # GET /projects/{project_id}/contributors/
        'post': 'create'         # POST /projects/{project_id}/contributors/
    }), name='contributors-list'),

    # Suppression d'un contributeur
    path('projects/<int:project_pk>/contributors/<int:pk>/', views.ContributorViewSet.as_view({
        'delete': 'destroy'      # DELETE /projects/{project_id}/contributors/{contributor_id}/
    }), name='contributors-detail'),


    # ================================
    # ISSUES
    # ================================

    # Liste et création des issues d'un projet
    path('projects/<int:project_pk>/issues/', views.IssueViewSet.as_view({
        'get': 'list',           # GET /projects/{project_id}/issues/
        'post': 'create'         # POST /projects/{project_id}/issues/
    }), name='issues-list'),

    # Détail, modification et suppression d'une issue
    path('projects/<int:project_pk>/issues/<int:pk>/', views.IssueViewSet.as_view({
        'get': 'retrieve',       # GET /projects/{project_id}/issues/{issue_id}/
        'put': 'update',         # PUT /projects/{project_id}/issues/{issue_id}/
        'patch': 'partial_update',  # PATCH /projects/{project_id}/issues/{issue_id}/
        'delete': 'destroy'      # DELETE /projects/{project_id}/issues/{issue_id}/
    }), name='issues-detail'),


    # ================================
    # COMMENTAIRES
    # ================================

    # Liste et création des commentaires d'une issue
    path('projects/<int:project_pk>/issues/<int:issue_pk>/comments/', views.CommentViewSet.as_view({
        'get': 'list',           # GET /projects/{project_id}/issues/{issue_id}/comments/
        'post': 'create'         # POST /projects/{project_id}/issues/{issue_id}/comments/
    }), name='comments-list'),

    # Détail, modification et suppression d'un commentaire
    path('projects/<int:project_pk>/issues/<int:issue_pk>/comments/<int:pk>/', views.CommentViewSet.as_view({
        'get': 'retrieve',       # GET /projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
        'put': 'update',         # PUT /projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
        'patch': 'partial_update',  # PATCH /projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
        'delete': 'destroy'      # DELETE /projects/{project_id}/issues/{issue_id}/comments/{comment_id}/
    }), name='comments-detail'),


    # ================================
    # RGPD - CONFORMITÉ
    # ================================

    # Export des données personnelles (RGPD Article 15)
    path('gdpr/export-my-data/', views.GDPRViewSet.as_view({
        'get': 'export_my_data'  # GET /gdpr/export-my-data/
    }), name='gdpr-export'),

    # Suppression du compte (RGPD Article 17)
    path('gdpr/delete-my-account/', views.GDPRViewSet.as_view({
        'delete': 'delete_my_account'  # DELETE /gdpr/delete-my-account/
    }), name='gdpr-delete'),
]
