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

## Routes Issues
| Méthode | URL | Description | Permissions |
|---------|-----|-------------|-------------|
| GET | `/api/projects/{id}/issues/` | Liste des issues du projet | Contributeur du projet |
| POST | `/api/projects/{id}/issues/` | Créer une nouvelle issue | Contributeur du projet |
| GET | `/api/projects/{id}/issues/{issue_id}/` | Détail d'une issue | Contributeur du projet |
| PUT | `/api/projects/{id}/issues/{issue_id}/` | Modifier complètement une issue | Auteur issue/projet |
| PATCH | `/api/projects/{id}/issues/{issue_id}/` | Modifier partiellement une issue | Auteur issue/projet |
| DELETE | `/api/projects/{id}/issues/{issue_id}/` | Supprimer une issue | Auteur issue/projet |

## Exemples de requêtes

### 1. Inscription
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "alice",
    "password": "password123",
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Dupont",
    "date_of_birth": "1995-01-01",
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```

### 2. Connexion
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "alice",
    "password": "password123"
}
```

### 3. Créer un projet
```http
POST /api/projects/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "name": "Mon Premier Projet",
    "description": "Description du projet",
    "type": "backend"
}
```

### 4. Ajouter un contributeur
```http
POST /api/projects/1/contributors/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "username": "bob"
}
```

### 5. Lister les contributeurs
```http
GET /api/projects/1/contributors/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 6. Retirer un contributeur
```http
DELETE /api/projects/1/contributors/2/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 7. Créer une issue
```http
POST /api/projects/1/issues/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "name": "Corriger le bug de connexion",
    "description": "Le système de connexion ne fonctionne pas correctement",
    "assignee_username": "bob",
    "priority": "HIGH",
    "tag": "BUG",
    "status": "TO_DO"
}
```

### 8. Lister les issues d'un projet
```http
GET /api/projects/1/issues/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 9. Modifier une issue
```http
PATCH /api/projects/1/issues/1/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "status": "IN_PROGRESS",
    "assignee_username": "alice"
}
```

### 10. Supprimer une issue
```http
DELETE /api/projects/1/issues/1/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Authentification JWT

Toutes les routes (sauf auth) nécessitent un token JWT dans le header :
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Paramètres des Issues

### Priorités disponibles :
- `LOW` : Faible
- `MEDIUM` : Moyenne (par défaut)
- `HIGH` : Élevée

### Types/Balises disponibles :
- `BUG` : Bug
- `FEATURE` : Fonctionnalité
- `TASK` : Tâche (par défaut)

### Statuts disponibles :
- `TO_DO` : À faire (par défaut)
- `IN_PROGRESS` : En cours
- `FINISHED` : Terminé

## Codes de statut HTTP

- `200 OK` : Succès (GET, PUT, PATCH)
- `201 Created` : Ressource créée (POST)
- `204 No Content` : Suppression réussie (DELETE)
- `400 Bad Request` : Données invalides
- `401 Unauthorized` : Token manquant ou invalide
- `403 Forbidden` : Permissions insuffisantes
- `404 Not Found` : Ressource non trouvée

## Permissions

### Niveaux d'accès :
1. **Public** : Routes d'authentification
2. **Authentifié** : Création de projets
3. **Contributeur** : Lecture des projets/contributeurs/issues, création d'issues
4. **Auteur** : Modification/suppression des projets, gestion des contributeurs
5. **Auteur issue/projet** : Modification/suppression des issues

### Règles spéciales :
- L'auteur d'un projet devient automatiquement contributeur
- L'auteur ne peut pas être retiré de ses propres projets
- Seuls les contributeurs voient les projets dans la liste
- Les issues ne peuvent être assignées qu'aux contributeurs du projet
- Seul l'auteur d'une issue ou l'auteur du projet peut modifier/supprimer l'issue