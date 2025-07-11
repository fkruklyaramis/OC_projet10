"""
Serializers pour l'API SoftDesk
Gère la conversion entre les objets Python/Django et les formats JSON pour l'API REST
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Project, Contributor, Issue, Comment


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
            'created_time': {'read_only': True},  # Auto-généré, pas modifiable
            'date_of_birth': {'required': True}  # Obligatoire pour l'API
        }

    def validate_date_of_birth(self, value):
        """
        Validation spécifique pour date_of_birth
        Obligatoire pour les inscriptions via API
        """
        if value is None:
            raise serializers.ValidationError("La date de naissance est obligatoire.")
        return value

    def create(self, validated_data):
        """
        Création d'un nouvel utilisateur
        - Extrait le mot de passe des données
        - Utilise create_user() pour le hash automatique du mot de passe
        - Respecte les validations RGPD (âge minimum 15 ans)
        """
        from django.core.exceptions import ValidationError

        password = validated_data.pop('password')  # Retire le mot de passe des données

        try:
            user = User.objects.create_user(**validated_data)  # Crée l'utilisateur
            user.set_password(password)  # Hash le mot de passe
            user.save()
            return user
        except ValidationError as e:
            # Transformer les erreurs du modèle en erreurs de serializer
            raise serializers.ValidationError({"date_of_birth": str(e)})

    # Validation d'âge gérée dans le modèle User.clean() - pas de duplication


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
        - L'ajout comme contributeur est géré dans la vue
        """
        # L'auteur est automatiquement défini comme l'utilisateur connecté
        validated_data['author'] = self.context['request'].user
        project = Project.objects.create(**validated_data)
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
        - Le projet est passé directement depuis la vue via save(project=project)
        - Vérifie qu'il n'est pas déjà contributeur
        """
        user = validated_data.pop('username')  # Récupère l'objet User validé
        project = validated_data.pop('project')  # Récupère le projet depuis save()

        # Double vérification : éviter les contributeurs en double
        if Contributor.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur de ce projet."
            )

        return Contributor.objects.create(user=user, project=project)


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'affichage et la gestion des Issues
    - Affiche les informations lisibles (noms au lieu d'IDs)
    - Gère les validations métier
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    # Choix disponibles pour les champs à choix multiples
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    tag_display = serializers.CharField(source='get_tag_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'name', 'description', 'project', 'project_name',
            'author', 'author_username', 'assignee', 'assignee_username',
            'priority', 'priority_display', 'tag', 'tag_display',
            'status', 'status_display', 'created_time', 'updated_time'
        ]
        read_only_fields = ['author', 'project', 'created_time', 'updated_time']

    def __init__(self, *args, **kwargs):
        """
        Initialisation dynamique pour limiter les assignés aux contributeurs du projet
        """
        super().__init__(*args, **kwargs)

        # Si on a un contexte avec le projet, limiter les assignés
        if 'project' in self.context:
            project = self.context['project']
            # Limiter le queryset aux contributeurs du projet
            self.fields['assignee'].queryset = User.objects.filter(
                contributions__project=project
            )

    def validate_assignee(self, value):
        """
        Validation pour s'assurer que l'assigné est contributeur du projet
        """
        if value and 'project' in self.context:
            project = self.context['project']
            if not project.contributors.filter(user=value).exists():
                raise serializers.ValidationError(
                    "L'utilisateur assigné doit être contributeur du projet."
                )
        return value


class IssueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la création d'Issues
    - Interface utilisateur simplifiée
    - Assigné par username (optionnel)
    """
    assignee_username = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        help_text="Username du contributeur à assigner (optionnel)"
    )

    class Meta:
        model = Issue
        fields = [
            'name', 'description', 'assignee_username',
            'priority', 'tag', 'status'
        ]

    def validate_assignee_username(self, value):
        """
        Validation du username de l'assigné
        """
        if not value:  # Si vide, c'est OK
            return None

        try:
            user = User.objects.get(username=value)
            # Vérifier que l'utilisateur est contributeur du projet
            project = self.context['project']
            if not project.contributors.filter(user=user).exists():
                raise serializers.ValidationError(
                    f"L'utilisateur '{value}' n'est pas contributeur de ce projet."
                )
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(f"L'utilisateur '{value}' n'existe pas.")

    def create(self, validated_data):
        """
        Création d'une Issue avec gestion de l'assigné
        """
        assignee = validated_data.pop('assignee_username', None)
        project = self.context['project']
        author = self.context['request'].user

        issue = Issue.objects.create(
            project=project,
            author=author,
            assignee=assignee,
            **validated_data
        )
        return issue


class IssueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des Issues
    - Permet de changer l'assigné par username
    - Maintient les validations
    """
    assignee_username = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
        help_text="Username du contributeur à assigner (laisser vide pour désassigner)"
    )

    class Meta:
        model = Issue
        fields = [
            'name', 'description', 'assignee_username',
            'priority', 'tag', 'status'
        ]

    def validate_assignee_username(self, value):
        """
        Validation du username de l'assigné pour la mise à jour
        """
        if not value:  # Si vide, désassigner
            return None

        try:
            user = User.objects.get(username=value)
            # Vérifier que l'utilisateur est contributeur du projet
            issue = self.instance
            if not issue.project.contributors.filter(user=user).exists():
                raise serializers.ValidationError(
                    f"L'utilisateur '{value}' n'est pas contributeur de ce projet."
                )
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(f"L'utilisateur '{value}' n'existe pas.")

    def update(self, instance, validated_data):
        """
        Mise à jour avec gestion de l'assigné
        """
        assignee = validated_data.pop('assignee_username', 'no_change')

        # Mettre à jour l'assigné seulement si le champ est fourni
        if assignee != 'no_change':
            instance.assignee = assignee

        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'affichage et la gestion des commentaires
    - Affiche les informations lisibles (noms au lieu d'IDs)
    - UUID en lecture seule
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    issue_name = serializers.CharField(source='issue.name', read_only=True)
    project_name = serializers.CharField(source='issue.project.name', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'description', 'issue', 'issue_name', 'project_name',
            'author', 'author_username', 'created_time'
        ]
        read_only_fields = ['id', 'author', 'issue', 'created_time']


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la création de commentaires
    - Interface utilisateur simplifiée
    - Validation de l'auteur comme contributeur
    """

    class Meta:
        model = Comment
        fields = ['description']

    def validate(self, data):
        """
        Validation globale pour vérifier les permissions
        """
        # L'issue et l'auteur sont passés via le contexte
        issue = self.context.get('issue')
        author = self.context.get('request').user

        if issue and author:
            # Vérifier que l'auteur est contributeur du projet
            if not issue.project.contributors.filter(user=author).exists():
                raise serializers.ValidationError(
                    "Vous devez être contributeur du projet pour commenter cette issue."
                )

        return data

    def create(self, validated_data):
        """
        Création d'un commentaire avec gestion automatique de l'issue et auteur
        """
        issue = self.context['issue']
        author = self.context['request'].user

        comment = Comment.objects.create(
            issue=issue,
            author=author,
            **validated_data
        )
        return comment


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des commentaires
    - Seule la description peut être modifiée
    """

    class Meta:
        model = Comment
        fields = ['description']
