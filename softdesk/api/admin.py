from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Ajout des champs personnalisés
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations RGPD', {
            'fields': ('date_of_birth', 'can_be_contacted', 'can_data_be_shared')
        }),
        ('Horodatage', {
            'fields': ('created_time',),
            'classes': ('collapse',)
        }),
    )

    # Champs en lecture seule
    readonly_fields = ('created_time',)

    # Ajout dans la liste d'affichage
    list_display = BaseUserAdmin.list_display + ('age', 'can_be_contacted', 'created_time')

    # Filtres
    list_filter = BaseUserAdmin.list_filter + ('can_be_contacted', 'can_data_be_shared', 'created_time')
