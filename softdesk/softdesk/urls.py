"""
URL configuration for softdesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Configuration du schéma OpenAPI pour Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="API SoftDesk",
        default_version='v1',
        description="""
        # API SoftDesk - Gestion de Projets Collaboratifs

        ## Description
        API REST pour la gestion collaborative de projets avec système de suivi d'issues et commentaires.

        ## Fonctionnalités principales
        - **Authentification JWT** : Inscription, connexion et gestion sécurisée des utilisateurs
        - **Gestion des projets** : CRUD complet avec permissions d'auteur
        - **Système de contributeurs** : Ajout/suppression de membres d'équipe
        - **Suivi des issues** : Création et gestion de tâches/bugs avec priorités
        - **Commentaires** : Communication sur les issues avec UUID unique

        ## Authentification
        Utilisez le token JWT dans le header : `Authorization: Bearer <your-token>`

        ## Permissions
        - **Public** : Inscription et connexion
        - **Authentifié** : Création de projets
        - **Contributeur** : Lecture des projets/issues/commentaires
        - **Auteur** : Modification/suppression complète
        """,
        terms_of_service="https://www.exemple.com/terms/",
        contact=openapi.Contact(email="contact@softdesk.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),

    # API SoftDesk
    path('api/', include('api.urls')),

    # === DOCUMENTATION API ===
    # Interface Swagger UI (interactive)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Interface ReDoc (documentation lisible)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Schéma JSON brut
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # Schéma YAML brut
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]
