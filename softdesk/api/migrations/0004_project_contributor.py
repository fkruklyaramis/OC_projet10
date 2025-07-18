# Generated by Django 5.2.3 on 2025-07-04 08:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom du projet')),
                ('description', models.TextField(verbose_name='Description')),
                ('type', models.CharField(choices=[('backend', 'Back-end'), ('frontend', 'Front-end'), ('ios', 'iOS'), ('android', 'Android')], max_length=20, verbose_name='Type')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_projects', to=settings.AUTH_USER_MODEL, verbose_name='Auteur')),
            ],
            options={
                'verbose_name': 'Projet',
                'verbose_name_plural': 'Projets',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributions', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributors', to='api.project', verbose_name='Projet')),
            ],
            options={
                'verbose_name': 'Contributeur',
                'verbose_name_plural': 'Contributeurs',
                'ordering': ['-created_time'],
                'unique_together': {('user', 'project')},
            },
        ),
    ]
