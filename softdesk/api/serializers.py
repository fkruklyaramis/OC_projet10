"""
Serializers pour l'API SoftDesk
Gère la conversion entre les objets Python/Django et les formats JSON pour l'API REST
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Project, Contributor


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle User personnalisé
    - Gère l'inscription et l'affichage des utilisateurs
    - Le mot de passe est write_only pour la sécurité
    """
    # Le mot de passe ne sera jamais retourné dans les réponses JSON (write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        # Champs exposés dans l'API
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'date_of_birth', 'can_be_contacted', 'can_data_be_shared',
                  'password', 'created_time']
        extra_kwargs = {
            'password': {'write_only': True},  # Sécurité : mot de passe jamais lu
            'created_time': {'read_only': True}  # Auto-généré, pas modifiable
        }

    def create(self, validated_data):
        """
        Création d'un nouvel utilisateur
        - Extrait le mot de passe des données
        - Utilise create_user() pour le hash automatique du mot de passe
        - Respecte les validations RGPD (âge minimum 15 ans)
        """
        password = validated_data.pop('password')  # Retire le mot de passe des données
        user = User.objects.create_user(**validated_data)  # Crée l'utilisateur
        user.set_password(password)  # Hash le mot de passe
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer pour l'authentification des utilisateurs
    - Valide les identifiants (username + password)
    - Retourne l'utilisateur authentifié pour la génération du JWT
    """
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validation globale des données de connexion
        - Vérifie que username et password sont fournis
        - Authentifie l'utilisateur avec Django
        - Vérifie que le compte est actif
        """
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Tentative d'authentification avec Django
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides')
            if not user.is_active:
                raise serializers.ValidationError('Compte désactivé')
            # Ajoute l'utilisateur aux données validées pour la vue
            data['user'] = user
        else:
            raise serializers.ValidationError('Username et password requis')

        return data


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Project
    - Gère la création et l'affichage des projets
    - L'auteur est automatiquement défini comme l'utilisateur connecté
    - Calcule le nombre de contributeurs pour l'affichage
    """
    # Affiche le username de l'auteur au lieu de son ID (plus lisible)
    author = serializers.StringRelatedField(read_only=True)
    # Champ calculé : nombre de contributeurs du projet
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'contributors_count', 'created_time']
        read_only_fields = ['author', 'created_time']  # Ces champs sont auto-générés

    def get_contributors_count(self, obj):
        """
        Méthode pour calculer le nombre de contributeurs
        Utilisée par le SerializerMethodField 'contributors_count'
        """
        return obj.contributors.count()

    def create(self, validated_data):
        """
        Création d'un nouveau projet
        - L'auteur devient automatiquement l'utilisateur connecté
        - L'auteur est automatiquement ajouté comme contributeur
        """
        # L'auteur est automatiquement défini comme l'utilisateur connecté
        validated_data['author'] = self.context['request'].user
        project = Project.objects.create(**validated_data)

        # L'auteur devient automatiquement contributeur du projet
        Contributor.objects.create(user=project.author, project=project)
        return project


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Contributor (lecture/affichage)
    - Affiche les relations User/Project de manière lisible
    - Utilisé pour lister les contributeurs d'un projet
    """
    # Affiche le username au lieu de l'ID utilisateur
    user_username = serializers.CharField(source='user.username', read_only=True)
    # Affiche le nom du projet au lieu de l'ID projet
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'user_username', 'project', 'project_name', 'created_time']
        read_only_fields = ['created_time']

    def validate(self, data):
        """
        Validation pour éviter les contributeurs en double
        Vérifie qu'un utilisateur n'est pas déjà contributeur du même projet
        """
        # Vérifier que l'utilisateur n'est pas déjà contributeur
        if Contributor.objects.filter(user=data['user'], project=data['project']).exists():
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur de ce projet."
            )
        return data


class ContributorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer spécialisé pour ajouter un contributeur à un projet
    - Interface simplifiée : seul le username est requis
    - Le projet est récupéré automatiquement depuis l'URL (contexte)
    - Validation automatique de l'existence de l'utilisateur
    """
    # Champ simplifié : juste le username au lieu de l'ID utilisateur
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Contributor
        fields = ['username']  # Seul le username est nécessaire

    def validate_username(self, value):
        """
        Validation du username fourni
        - Vérifie que l'utilisateur existe en base de données
        - Retourne l'objet User pour la création
        """
        try:
            user = User.objects.get(username=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")

    def create(self, validated_data):
        """
        Création d'un nouveau contributeur
        - Récupère l'utilisateur depuis le username validé
        - Récupère le projet depuis le contexte (passé par la vue)
        - Vérifie qu'il n'est pas déjà contributeur
        """
        user = validated_data.pop('username')  # Récupère l'objet User validé
        project = self.context['project']  # Récupère le projet depuis la vue
        validated_data['user'] = user

        # Double vérification : éviter les contributeurs en double
        if Contributor.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur de ce projet."
            )

        return Contributor.objects.create(user=user, project=project)
