from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date


class User(AbstractUser):
    """
    Modèle User personnalisé héritant d'AbstractUser
    Respecte les normes RGPD avec validation d'âge et choix de confidentialité
    """
    # Champs obligatoires pour RGPD
    date_of_birth = models.DateField(
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
        Validation personnalisée pour vérifier l'âge minimum de 15 ans
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
        Surcharge de save pour inclure la validation
        """
        self.clean()
        super().save(*args, **kwargs)

    @property
    def age(self):
        """
        Calcule l'âge de l'utilisateur
        """
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_time']
