# API SoftDesk - Documentation des Routes

## Routes Authentication & Users
| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/register/` | Inscription d'un nouvel utilisateur |
| POST | `/api/auth/login/` | Connexion (retourne JWT tokens) |
| POST | `/api/auth/refresh/` | Renouveler l'access token |
| GET | `/api/auth/profile/` | Profil de l'utilisateur connecté |

## Routes Projects
| Méthode | URL | Description | Permissions |
|---------|-----|-------------|-------------|
| GET | `/api/projects/` | Liste des projets | Contributeur uniquement |
| POST | `/api/projects/` | Créer un projet | Utilisateur authentifié |
| GET | `/api/projects/{id}/` | Détail d'un projet | Contributeur uniquement |
| PUT | `/api/projects/{id}/` | Modifier complètement un projet | Auteur seulement |
| PATCH | `/api/projects/{id}/` | Modifier partiellement un projet | Auteur seulement |
| DELETE | `/api/projects/{id}/` | Supprimer un projet | Auteur seulement |

## Routes Contributors
| Méthode | URL | Description | Permissions |
|---------|-----|-------------|-------------|
| GET | `/api/projects/{id}/contributors/` | Liste des contributeurs | Contributeur du projet |
| POST | `/api/projects/{id}/contributors/` | Ajouter un contributeur | Auteur seulement |
| DELETE | `/api/projects/{id}/contributors/{user_id}/` | Retirer un contributeur | Auteur seulement |