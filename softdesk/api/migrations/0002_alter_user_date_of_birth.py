# Generated by Django 5.2.3 on 2025-07-02 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(blank=True, help_text="Requis pour vérifier l'âge minimum de 15 ans", null=True, verbose_name='Date de naissance'),
        ),
    ]
