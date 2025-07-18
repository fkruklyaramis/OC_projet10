"""
Configuration de l'interface d'administration Django pour l'API SoftDesk

Ce module définit la configuration de l'interface d'administration Django
pour tous les modèles de l'application SoftDesk.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Contributor, Issue, Comment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuration de l'admin pour le modèle User personnalisé.

    Étend BaseUserAdmin pour inclure les champs RGPD spécifiques
    à l'application (date_of_birth, consentements).
    """
    # Ajout des champs personnalisés aux fieldsets existants
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations RGPD', {
            'fields': ('date_of_birth', 'can_be_contacted', 'can_data_be_shared')
        }),
        ('Horodatage', {
            'fields': ('created_time',),
            'classes': ('collapse',)  # Section repliable
        }),
    )

    # Ajout des champs pour la création d'utilisateur
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations RGPD', {
            'fields': ('date_of_birth', 'can_be_contacted', 'can_data_be_shared')
        }),
    )

    # Champs en lecture seule (auto-générés)
    readonly_fields = ('created_time',)

    # Colonnes affichées dans la liste des utilisateurs
    list_display = BaseUserAdmin.list_display + ('age', 'can_be_contacted', 'created_time')

    # Filtres disponibles dans la barre latérale
    list_filter = BaseUserAdmin.list_filter + ('can_be_contacted', 'can_data_be_shared', 'created_time')

    # Champs de recherche
    search_fields = BaseUserAdmin.search_fields + ('email',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Project.

    Fournit une interface complète pour gérer les projets avec
    affichage du nombre de contributeurs et filtres par type.
    """
    # Colonnes affichées dans la liste des projets
    list_display = ('name', 'type', 'author', 'contributors_count', 'created_time')

    # Filtres disponibles
    list_filter = ('type', 'created_time', 'author')

    # Champs de recherche
    search_fields = ('name', 'description', 'author__username')

    # Champs en lecture seule
    readonly_fields = ('created_time',)

    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Informations du projet', {
            'fields': ('name', 'description', 'type')
        }),
        ('Métadonnées', {
            'fields': ('author', 'created_time'),
            'classes': ('collapse',)
        }),
    )

    # Filtres par date
    date_hierarchy = 'created_time'

    # Nombre d'éléments par page
    list_per_page = 25

    def contributors_count(self, obj):
        """
        Calcule et affiche le nombre de contributeurs du projet.

        Args:
            obj (Project): Instance du modèle Project

        Returns:
            int: Nombre de contributeurs
        """
        return obj.contributors.count()
    contributors_count.short_description = 'Contributeurs'
    contributors_count.admin_order_field = 'contributors'


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Contributor.

    Gère la relation many-to-many entre User et Project avec
    prévention des doublons et autocomplete pour les performances.
    """
    # Colonnes affichées
    list_display = ('user', 'project', 'created_time')

    # Filtres disponibles
    list_filter = ('created_time', 'project__type')

    # Champs de recherche
    search_fields = ('user__username', 'project__name')

    # Champs en lecture seule
    readonly_fields = ('created_time',)

    # Organisation des champs
    fieldsets = (
        ('Association', {
            'fields': ('user', 'project')
        }),
        ('Métadonnées', {
            'fields': ('created_time',),
            'classes': ('collapse',)
        }),
    )

    # Filtres par date
    date_hierarchy = 'created_time'

    # Autocomplete pour les relations (améliore les performances)
    autocomplete_fields = ('user', 'project')

    # Prévention des doublons via l'admin
    def get_readonly_fields(self, request, obj=None):
        """
        Configure les champs en lecture seule selon le contexte.

        Empêche la modification de user et project après création
        pour éviter les incohérences dans les relations.

        Args:
            request: Requête HTTP courante
            obj (Contributor or None): Instance de Contributor (None lors de la création)

        Returns:
            tuple: Champs en lecture seule
        """
        if obj:  # Si on modifie un contributeur existant
            return self.readonly_fields + ('user', 'project')
        return self.readonly_fields


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Issue.

    Interface complète pour gérer les issues/tâches avec workflow
    de statuts et actions en lot pour la gestion de projet.
    """
    # Colonnes affichées dans la liste
    list_display = (
        'name', 'project', 'author', 'assignee',
        'priority', 'tag', 'status', 'created_time'
    )

    # Filtres disponibles dans la sidebar
    list_filter = (
        'priority', 'tag', 'status', 'project__type',
        'created_time', 'updated_time'
    )

    # Champs de recherche
    search_fields = (
        'name', 'description', 'project__name',
        'author__username', 'assignee__username'
    )

    # Organisation des champs en sections
    fieldsets = (
        ('Informations de l\'issue', {
            'fields': ('name', 'description')
        }),
        ('Assignation', {
            'fields': ('project', 'author', 'assignee')
        }),
        ('Classification', {
            'fields': ('priority', 'tag', 'status'),
            'classes': ('wide',)
        }),
        ('Métadonnées', {
            'fields': ('created_time', 'updated_time'),
            'classes': ('collapse',)
        }),
    )

    # Champs en lecture seule
    readonly_fields = ('created_time', 'updated_time')

    # Filtres par date
    date_hierarchy = 'created_time'

    # Tri par défaut
    ordering = ('-created_time',)

    # Pagination
    list_per_page = 25

    # Autocomplete pour les relations (améliore les performances)
    autocomplete_fields = ('project', 'author', 'assignee')

    # Actions personnalisées
    actions = ['mark_as_to_do', 'mark_as_in_progress', 'mark_as_finished']

    def mark_as_to_do(self, request, queryset):
        """
        Action en lot pour marquer les issues sélectionnées comme 'À faire'.

        Args:
            request: Requête HTTP de l'admin
            queryset: Issues sélectionnées par l'utilisateur

        Returns:
            None: Affiche un message de confirmation via self.message_user
        """
        updated = queryset.update(status='TO_DO')
        self.message_user(request, f'{updated} issue(s) marquée(s) comme "À faire".')
    mark_as_to_do.short_description = "Marquer comme 'À faire'"

    def mark_as_in_progress(self, request, queryset):
        """
        Action en lot pour marquer les issues sélectionnées comme 'En cours'.

        Args:
            request: Requête HTTP de l'admin
            queryset: Issues sélectionnées par l'utilisateur

        Returns:
            None: Affiche un message de confirmation via self.message_user
        """
        updated = queryset.update(status='IN_PROGRESS')
        self.message_user(request, f'{updated} issue(s) marquée(s) comme "En cours".')
    mark_as_in_progress.short_description = "Marquer comme 'En cours'"

    def mark_as_finished(self, request, queryset):
        """
        Action en lot pour marquer les issues sélectionnées comme 'Terminé'.

        Args:
            request: Requête HTTP de l'admin
            queryset: Issues sélectionnées par l'utilisateur

        Returns:
            None: Affiche un message de confirmation via self.message_user
        """
        updated = queryset.update(status='FINISHED')
        self.message_user(request, f'{updated} issue(s) marquée(s) comme "Terminé".')
    mark_as_finished.short_description = "Marquer comme 'Terminé'"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Comment.

    Interface pour gérer les commentaires des issues avec affichage
    raccourci du contenu et protection des relations après création.
    """
    # Colonnes affichées dans la liste
    list_display = (
        'short_description', 'issue', 'author', 'created_time'
    )

    # Filtres disponibles dans la sidebar
    list_filter = (
        'issue__project', 'issue__tag', 'issue__status',
        'created_time', 'author'
    )

    # Champs de recherche
    search_fields = (
        'description', 'issue__name', 'author__username',
        'issue__project__name'
    )

    # Organisation des champs en sections
    fieldsets = (
        ('Contenu du commentaire', {
            'fields': ('description',)
        }),
        ('Références', {
            'fields': ('issue', 'author')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_time'),
            'classes': ('collapse',)
        }),
    )

    # Champs en lecture seule
    readonly_fields = ('id', 'created_time')

    # Filtres par date
    date_hierarchy = 'created_time'

    # Tri par défaut
    ordering = ('-created_time',)

    # Pagination
    list_per_page = 25

    # Autocomplete pour les relations
    autocomplete_fields = ('issue', 'author')

    def short_description(self, obj):
        """
        Affiche une version tronquée de la description du commentaire.

        Args:
            obj (Comment): Instance du modèle Comment

        Returns:
            str: Description tronquée à 50 caractères avec "..." si nécessaire
        """
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    short_description.short_description = "Description"

    def get_readonly_fields(self, request, obj=None):
        """
        Configure les champs en lecture seule selon le contexte.

        Empêche la modification de issue et author après création
        pour préserver l'intégrité des discussions.

        Args:
            request: Requête HTTP courante
            obj (Comment or None): Instance de Comment (None lors de la création)

        Returns:
            tuple: Champs en lecture seule
        """
        if obj:  # En modification
            return self.readonly_fields + ('issue', 'author')
        return self.readonly_fields
