from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Project, Contributor


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'date_of_birth', 'can_be_contacted', 'can_data_be_shared',
                  'password', 'created_time']
        extra_kwargs = {
            'password': {'write_only': True},
            'created_time': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides')
            if not user.is_active:
                raise serializers.ValidationError('Compte désactivé')
            data['user'] = user
        else:
            raise serializers.ValidationError('Username et password requis')

        return data


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    contributors_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'contributors_count', 'created_time']
        read_only_fields = ['author', 'created_time']

    def get_contributors_count(self, obj):
        return obj.contributors.count()

    def create(self, validated_data):
        # L'auteur est automatiquement défini comme l'utilisateur connecté
        validated_data['author'] = self.context['request'].user
        project = Project.objects.create(**validated_data)

        # L'auteur devient automatiquement contributeur
        Contributor.objects.create(user=project.author, project=project)
        return project


class ContributorSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Contributor
        fields = ['id', 'user', 'user_username', 'project', 'project_name', 'created_time']
        read_only_fields = ['created_time']

    def validate(self, data):
        # Vérifier que l'utilisateur n'est pas déjà contributeur
        if Contributor.objects.filter(user=data['user'], project=data['project']).exists():
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur de ce projet."
            )
        return data


class ContributorCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour ajouter un contributeur (seulement username nécessaire)
    """
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Contributor
        fields = ['username']

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")

    def create(self, validated_data):
        user = validated_data.pop('username')
        project = self.context['project']
        validated_data['user'] = user
        # Vérifier que l'utilisateur n'est pas déjà contributeur
        if Contributor.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError(
                "Cet utilisateur est déjà contributeur de ce projet."
            )

        return Contributor.objects.create(user=user, project=project)
