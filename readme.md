### Routes Projects
GET /api/projects/                          # Liste des projets
POST /api/projects/                         # Créer un projet
GET /api/projects/{id}/                     # Détail d'un projet
PUT /api/projects/{id}/                     # Modifier un projet (auteur seulement)
DELETE /api/projects/{id}/                  # Supprimer un projet (auteur seulement)

### Routes Contributors
GET /api/projects/{id}/contributors/        # Liste des contributeurs
POST /api/projects/{id}/add_contributor/    # Ajouter un contributeur (auteur seulement)
DELETE /api/projects/{id}/remove_contributor/{user_id}/  # Retirer un contributeur (auteur seulement)