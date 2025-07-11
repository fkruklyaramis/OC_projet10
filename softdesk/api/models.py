"""
Modèles de données pour l'API SoftDesk

Ce module définit tous les modèles Django pour l'application de gestion
de projets collaboratifs avec système de tickets et commentaires.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
import uuid


class User(AbstractUser):
    """
    Modèle User personnalisé avec conformité RGPD.

    Étend AbstractUser pour ajouter la validation d'âge minimum (15 ans)
    et les consentements RGPD requis.
    """
    # Champs obligatoires pour RGPD
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance",
        help_text="Requis pour vérifier l'âge minimum de 15 ans"
    )

    # Choix de confidentialité RGPD
    can_be_contacted = models.BooleanField(
        default=True,
        verbose_name="Peut être contacté",
        help_text="L'utilisateur accepte d'être contacté"
    )

    can_data_be_shared = models.BooleanField(
        default=False,
        verbose_name="Partage des données autorisé",
        help_text="L'utilisateur autorise le partage de ses données"
    )

    # Horodatage requis par les spécifications
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    def clean(self):
        """
        Valide l'âge minimum de 15 ans selon les exigences RGPD.

        Raises:
            ValidationError: Si l'utilisateur a moins de 15 ans
        """
        super().clean()
        if self.date_of_birth:
            today = date.today()
            age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if age < 15:
                raise ValidationError(
                    "L'utilisateur doit avoir au moins 15 ans selon les normes RGPD."
                )

    def save(self, *args, **kwargs):
        """
        Sauvegarde avec validation automatique de l'âge.

        Args:
            *args: Arguments positionnels pour la méthode save parente
            **kwargs: Arguments nommés pour la méthode save parente

        Raises:
            ValidationError: Si la validation clean() échoue
        """
        self.clean()
        super().save(*args, **kwargs)

    @property
    def age(self):
        """
        Calcule l'âge actuel de l'utilisateur.

        Returns:
            int or None: L'âge en années ou None si pas de date de naissance

        Note:
            Prend en compte les mois et jours pour un calcul précis
        """
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def __str__(self):
        """
        Représentation textuelle de l'utilisateur.

        Returns:
            str: Le nom d'utilisateur (username)
        """
        return self.username

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_time']


class Project(models.Model):
    """
    Modèle Project pour les projets collaboratifs.

    Représente un projet de développement avec contributeurs,
    issues et système de commentaires.
    """
    TYPE_CHOICES = [
        ('backend', 'Back-end'),
        ('frontend', 'Front-end'),
        ('ios', 'iOS'),
        ('android', 'Android'),
    ]

    name = models.CharField(max_length=255, verbose_name="Nom du projet")
    description = models.TextField(verbose_name="Description")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_projects',
        verbose_name="Auteur"
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    def __str__(self):
        """
        Représentation textuelle du projet.

        Returns:
            str: Le nom du projet
        """
        return self.name

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-created_time']


class Contributor(models.Model):
    """
    Modèle Contributor pour la relation many-to-many User-Project.

    Associe un utilisateur à un projet en tant que contributeur.
    Un utilisateur peut contribuer à plusieurs projets.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contributions',
        verbose_name="Utilisateur"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contributors',
        verbose_name="Projet"
    )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Contributeur"
        verbose_name_plural = "Contributeurs"
        unique_together = ('user', 'project')  # Un utilisateur ne peut être contributeur qu'une fois par projet
        ordering = ['-created_time']

    def __str__(self):
        """
        Représentation textuelle de la relation contributeur.

        Returns:
            str: Format "username - nom_projet"
        """
        return f"{self.user.username} - {self.project.name}"


class Issue(models.Model):
    """
    Modèle Issue pour les tickets/tâches d'un projet.

    Représente une tâche, bug ou fonctionnalité à développer
    avec workflow de statuts et assignation.
    """

    # Choix pour la priorité
    PRIORITY_CHOICES = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
    ]

    # Choix pour les balises/types
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Fonctionnalité'),
        ('TASK', 'Tâche'),
    ]

    # Choix pour le statut
    STATUS_CHOICES = [
        ('TO_DO', 'À faire'),
        ('IN_PROGRESS', 'En cours'),
        ('FINISHED', 'Terminé'),
    ]

    # Champs obligatoires
    name = models.CharField(max_length=255, verbose_name="Nom de l'issue")
    description = models.TextField(verbose_name="Description")

    # Relation avec le projet
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='issues',
        verbose_name="Projet"
    )

    # Auteur de l'issue (contributeur qui l'a créée)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_issues',
        verbose_name="Auteur"
    )

    # Assigné à (contributeur responsable de l'issue)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        verbose_name="Assigné à"
    )

    # Priorité de l'issue
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name="Priorité"
    )

    # Balise/Type de l'issue
    tag = models.CharField(
        max_length=10,
        choices=TAG_CHOICES,
        default='TASK',
        verbose_name="Type"
    )

    # Statut de progression
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='TO_DO',
        verbose_name="Statut"
    )

    # Horodatage
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"
        ordering = ['-created_time']

    def __str__(self):
        """
        Représentation textuelle de l'issue.

        Returns:
            str: Format "nom_issue - nom_projet"
        """
        return f"{self.name} - {self.project.name}"

    def clean(self):
        """
        Valide que l'assigné est contributeur du projet.

        Raises:
            ValidationError: Si l'assigné n'est pas contributeur du projet
        """
        super().clean()
        if self.assignee and self.project:
            if not self.project.contributors.filter(user=self.assignee).exists():
                raise ValidationError(
                    "L'utilisateur assigné doit être contributeur du projet."
                )


class Comment(models.Model):
    """
    Modèle Comment pour les commentaires sur les issues.

    Permet la communication entre contributeurs sur les issues
    avec identifiant UUID unique.
    """

    # Identifiant unique UUID pour référencer le commentaire
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant unique"
    )

    # Description du commentaire
    description = models.TextField(
        verbose_name="Description du commentaire"
    )

    # Relation avec l'issue
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Issue"
    )

    # Auteur du commentaire (contributeur qui l'a écrit)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_comments',
        verbose_name="Auteur"
    )

    # Horodatage
    created_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-created_time']

    def __str__(self):
        """
        Représentation textuelle du commentaire.

        Returns:
            str: Format "Commentaire de username sur nom_issue"
        """
        return f"Commentaire de {self.author.username} sur {self.issue.name}"

    def clean(self):
        """
        Valide que l'auteur est contributeur du projet de l'issue.

        Raises:
            ValidationError: Si l'auteur n'est pas contributeur du projet
        """
        super().clean()
        if self.author and self.issue and self.issue.project:
            if not self.issue.project.contributors.filter(user=self.author).exists():
                raise ValidationError(
                    "L'auteur du commentaire doit être contributeur du projet."
                )
