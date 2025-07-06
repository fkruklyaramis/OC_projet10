### Routes Authentication & Users
POST /api/auth/register/                    # Inscription d'un nouvel utilisateur
POST /api/auth/login/                       # Connexion (retourne JWT tokens)
POST /api/auth/refresh/                     # Renouveler l'access token
GET /api/auth/profile/                      # Profil de l'utilisateur connecté


### Routes Projects
GET /api/projects/                          # Liste des projets
POST /api/projects/                         # Créer un projet
GET /api/projects/{id}/                     # Détail d'un projet
PUT /api/projects/{id}/                     # Modifier un projet (auteur seulement)
DELETE /api/projects/{id}/                  # Supprimer un projet (auteur seulement)

### Routes Contributors
GET /api/projects/{id}/contributors/        # Liste des contributeurs
POST /api/projects/{id}/add_contributor/    # Ajouter un contributeur (auteur only)
DELETE /api/projects/{id}/remove_contributor/{user_id}/  # Retirer un contributeur (auteur only)