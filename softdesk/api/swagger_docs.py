"""
Documentation Swagger pour l'API SoftDesk
Centralise toutes les définitions de documentation pour maintenir la lisibilité des vues
"""

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserSerializer, LoginSerializer, ProjectSerializer,
    ContributorSerializer, IssueSerializer, CommentSerializer,
    IssueCreateSerializer, CommentCreateSerializer
)

# ===============================
# AUTHENTIFICATION
# ===============================

register_docs = swagger_auto_schema(
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
    }
)

login_docs = swagger_auto_schema(
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
    }
)

profile_docs = swagger_auto_schema(
    method='get',
    operation_summary="Profil utilisateur connecté",
    operation_description="Retourne les informations de l'utilisateur authentifié",
    responses={
        200: UserSerializer,
        401: "Token manquant ou invalide"
    }
)

refresh_token_docs = swagger_auto_schema(
    operation_summary="Rafraîchir le token JWT",
    operation_description="""
    Génère un nouveau token d'accès à partir du token de rafraîchissement.
    Le token de rafraîchissement doit être valide et non expiré.
    """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Token de rafraîchissement'
            )
        },
        required=['refresh']
    ),
    responses={
        200: openapi.Response(
            description="Token rafraîchi avec succès",
            examples={
                "application/json": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                }
            }
        ),
        401: "Token de rafraîchissement invalide ou expiré"
    }
)

# ===============================
# PROJETS
# ===============================

project_list_docs = swagger_auto_schema(
    operation_summary="Liste des projets",
    operation_description="Retourne la liste des projets où l'utilisateur est contributeur",
    responses={200: ProjectSerializer(many=True)}
)

project_create_docs = swagger_auto_schema(
    operation_summary="Créer un projet",
    operation_description="""
    Crée un nouveau projet. L'utilisateur devient automatiquement
    auteur et contributeur du projet.
    """,
    responses={
        201: ProjectSerializer,
        400: "Données invalides"
    }
)

project_retrieve_docs = swagger_auto_schema(
    operation_summary="Détail d'un projet",
    operation_description="Affiche les détails d'un projet (contributeurs uniquement)",
    responses={
        200: ProjectSerializer,
        403: "Accès refusé (non-contributeur)",
        404: "Projet non trouvé"
    }
)

project_update_docs = swagger_auto_schema(
    operation_summary="Modifier un projet (PUT)",
    operation_description="Modifie complètement un projet (auteur uniquement)",
    request_body=ProjectSerializer,
    responses={
        200: ProjectSerializer,
        403: "Accès refusé (non-auteur)",
        404: "Projet non trouvé"
    }
)

project_partial_update_docs = swagger_auto_schema(
    operation_summary="Modifier un projet (PATCH)",
    operation_description="Modifie partiellement un projet (auteur uniquement)",
    request_body=ProjectSerializer,
    responses={
        200: ProjectSerializer,
        403: "Accès refusé (non-auteur)",
        404: "Projet non trouvé"
    }
)

project_destroy_docs = swagger_auto_schema(
    operation_summary="Supprimer un projet",
    operation_description="Supprime définitivement un projet (auteur uniquement)",
    responses={
        204: "Projet supprimé",
        403: "Accès refusé (non-auteur)",
        404: "Projet non trouvé"
    }
)

# ===============================
# CONTRIBUTEURS
# ===============================

contributor_list_docs = swagger_auto_schema(
    operation_summary="Liste des contributeurs",
    operation_description="Liste tous les contributeurs d'un projet",
    responses={
        200: ContributorSerializer(many=True),
        403: "Accès refusé (non-contributeur)",
        404: "Projet non trouvé"
    },
    tags=['contributors']
)

contributor_add_docs = swagger_auto_schema(
    operation_summary="Ajouter un contributeur",
    operation_description="Ajoute un utilisateur comme contributeur du projet (auteur uniquement)",
    responses={
        201: ContributorSerializer,
        400: "Utilisateur déjà contributeur ou non trouvé",
        403: "Accès refusé (non-auteur)"
    },
    tags=['contributors']
)

contributor_remove_docs = swagger_auto_schema(
    operation_summary="Retirer un contributeur",
    operation_description="Retire un contributeur du projet (auteur uniquement)",
    responses={
        204: "Contributeur retiré",
        403: "Accès refusé (non-auteur)",
        404: "Contributeur non trouvé"
    },
    tags=['contributors']
)

# ===============================
# ISSUES
# ===============================

issue_list_docs = swagger_auto_schema(
    operation_summary="Liste des issues",
    operation_description="Liste toutes les issues d'un projet",
    responses={
        200: IssueSerializer(many=True),
        403: "Accès refusé (non-contributeur)"
    },
    tags=['issues']
)

issue_create_docs = swagger_auto_schema(
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
    tags=['issues']
)

issue_retrieve_docs = swagger_auto_schema(
    operation_summary="Détail d'une issue",
    operation_description="Affiche les détails d'une issue",
    responses={
        200: IssueSerializer,
        403: "Accès refusé (non-contributeur)",
        404: "Issue non trouvée"
    },
    tags=['issues']
)

issue_update_docs = swagger_auto_schema(
    operation_summary="Modifier une issue (PUT)",
    operation_description="Modifie complètement une issue (auteur de l'issue ou du projet)",
    responses={
        200: IssueSerializer,
        403: "Accès refusé",
        404: "Issue non trouvée"
    },
    tags=['issues']
)

issue_partial_update_docs = swagger_auto_schema(
    operation_summary="Modifier une issue (PATCH)",
    operation_description="Modifie partiellement une issue (auteur de l'issue ou du projet)",
    responses={
        200: IssueSerializer,
        403: "Accès refusé",
        404: "Issue non trouvée"
    },
    tags=['issues']
)

issue_destroy_docs = swagger_auto_schema(
    operation_summary="Supprimer une issue",
    operation_description="Supprime définitivement une issue (auteur de l'issue ou du projet)",
    responses={
        204: "Issue supprimée",
        403: "Accès refusé",
        404: "Issue non trouvée"
    },
    tags=['issues']
)

# ===============================
# COMMENTAIRES
# ===============================

comment_list_docs = swagger_auto_schema(
    operation_summary="Liste des commentaires",
    operation_description="Liste tous les commentaires d'une issue",
    responses={
        200: CommentSerializer(many=True),
        403: "Accès refusé (non-contributeur)"
    },
    tags=['comments']
)

comment_create_docs = swagger_auto_schema(
    operation_summary="Créer un commentaire",
    operation_description="Ajoute un commentaire à une issue (contributeurs uniquement)",
    request_body=CommentCreateSerializer,
    responses={
        201: CommentSerializer,
        400: "Description requise",
        403: "Accès refusé (non-contributeur)"
    },
    tags=['comments']
)

comment_retrieve_docs = swagger_auto_schema(
    operation_summary="Détail d'un commentaire",
    operation_description="Affiche les détails d'un commentaire spécifique",
    responses={
        200: CommentSerializer,
        403: "Accès refusé (non-contributeur)",
        404: "Commentaire non trouvé"
    },
    tags=['comments']
)

comment_update_docs = swagger_auto_schema(
    operation_summary="Modifier un commentaire (PUT)",
    operation_description="Modifie complètement un commentaire (auteur uniquement)",
    responses={
        200: CommentSerializer,
        403: "Accès refusé (non-auteur)",
        404: "Commentaire non trouvé"
    },
    tags=['comments']
)

comment_partial_update_docs = swagger_auto_schema(
    operation_summary="Modifier un commentaire (PATCH)",
    operation_description="Modifie partiellement un commentaire (auteur uniquement)",
    responses={
        200: CommentSerializer,
        403: "Accès refusé (non-auteur)",
        404: "Commentaire non trouvé"
    },
    tags=['comments']
)

comment_destroy_docs = swagger_auto_schema(
    operation_summary="Supprimer un commentaire",
    operation_description="Supprime définitivement un commentaire (auteur uniquement)",
    responses={
        204: "Commentaire supprimé",
        403: "Accès refusé (non-auteur)",
        404: "Commentaire non trouvé"
    },
    tags=['comments']
)

# ===============================
# RGPD
# ===============================

rgpd_export_docs = swagger_auto_schema(
    operation_summary="Exporter mes données (RGPD)",
    operation_description="""
    RGPD Article 15 - Droit d'accès aux données personnelles.
    Télécharge toutes les données personnelles de l'utilisateur au format JSON.
    """,
    responses={
        200: "Données personnelles au format JSON",
        401: "Non authentifié"
    }
)

rgpd_delete_docs = swagger_auto_schema(
    operation_summary="Supprimer mon compte (RGPD)",
    operation_description="""
    RGPD Article 17 - Droit à l'oubli.
    Supprime définitivement le compte utilisateur et anonymise les données liées.
    Cette action est irréversible.
    """,
    responses={
        204: "Compte supprimé avec succès",
        401: "Non authentifié"
    }
)
