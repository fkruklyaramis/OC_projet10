"""
Configuration de l'interface d'administration Django pour l'API SoftDesk
Définit l'affichage et la gestion des modèles dans l'admin Django
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Contributor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Configuration de l'admin pour le modèle User personnalisé
    Étend l'UserAdmin par défaut avec les champs RGPD
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
    Configuration de l'admin pour le modèle Project
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
        """Affiche le nombre de contributeurs"""
        return obj.contributors.count()
    contributors_count.short_description = 'Contributeurs'
    contributors_count.admin_order_field = 'contributors'


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """
    Configuration de l'admin pour le modèle Contributor
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
        if obj:  # Si on modifie un contributeur existant
            return self.readonly_fields + ('user', 'project')
        return self.readonly_fields
