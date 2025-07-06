# API SoftDesk - Documentation des Routes

## � Installation et Démarrage

### Option 1 : Installation locale avec Pipenv

```bash
# Cloner le projet
git clone <votre-repo>
cd OC_projet10

# Installer les dépendances
pipenv install

# Activer l'environnement virtuel
pipenv shell

# Appliquer les migrations
cd softdesk
python manage.py migrate

# Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### Option 2 : Installation avec Docker 🐳

```bash
# Construire l'image Docker
docker build -t softdesk-api .

# Lancer le conteneur
docker run -d --name softdesk -p 8000:8000 softdesk-api

# Voir les logs (optionnel)
docker logs -f softdesk

# Arrêter le conteneur
docker stop softdesk
```

**Dockerfile inclus** : Le projet contient un Dockerfile prêt à l'emploi pour une containerisation simple et efficace.

## �📚 Documentation Interactive

**Interface Swagger disponible sur :** http://localhost:8000/doc/

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

## Routes Comments
| Méthode | URL | Description | Permissions |
|---------|-----|-------------|-------------|
| GET | `/api/projects/{id}/issues/{issue_id}/comments/` | Liste des commentaires de l'issue | Contributeur du projet |
| POST | `/api/projects/{id}/issues/{issue_id}/comments/` | Créer un nouveau commentaire | Contributeur du projet |
| GET | `/api/projects/{id}/issues/{issue_id}/comments/{uuid}/` | Détail d'un commentaire | Contributeur du projet |
| PUT | `/api/projects/{id}/issues/{issue_id}/comments/{uuid}/` | Modifier complètement un commentaire | Auteur commentaire |
| PATCH | `/api/projects/{id}/issues/{issue_id}/comments/{uuid}/` | Modifier partiellement un commentaire | Auteur commentaire |
| DELETE | `/api/projects/{id}/issues/{issue_id}/comments/{uuid}/` | Supprimer un commentaire | Auteur commentaire |

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

### 11. Créer un commentaire
```http
POST /api/projects/1/issues/1/comments/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "description": "Je pense que ce bug vient de la validation des formulaires. Il faudrait vérifier les champs email."
}
```

### 12. Lister les commentaires d'une issue
```http
GET /api/projects/1/issues/1/comments/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 13. Modifier un commentaire
```http
PATCH /api/projects/1/issues/1/comments/550e8400-e29b-41d4-a716-446655440000/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "description": "Après investigation, le bug vient effectivement de la validation email. J'ai trouvé la solution."
}
```

### 14. Supprimer un commentaire
```http
DELETE /api/projects/1/issues/1/comments/550e8400-e29b-41d4-a716-446655440000/
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
3. **Contributeur** : Lecture des projets/contributeurs/issues/comments, création d'issues et comments
4. **Auteur** : Modification/suppression des projets, gestion des contributeurs
5. **Auteur issue/projet** : Modification/suppression des issues
6. **Auteur commentaire** : Modification/suppression des commentaires

### Règles spéciales :
- L'auteur d'un projet devient automatiquement contributeur
- L'auteur ne peut pas être retiré de ses propres projets
- Seuls les contributeurs voient les projets dans la liste
- Les issues ne peuvent être assignées qu'aux contributeurs du projet
- Seul l'auteur d'une issue ou l'auteur du projet peut modifier/supprimer l'issue
- Seul l'auteur d'un commentaire peut modifier/supprimer son commentaire
- Les commentaires utilisent des UUID comme identifiants uniques
- Les commentaires sont triés par date de création (plus récent en premier)

## 📚 Documentation API Interactive (Swagger)

L'API SoftDesk dispose d'une documentation interactive complète accessible via Swagger UI :

### 🌐 URLs de documentation disponibles :
- **📖 Documentation interactive (Swagger UI)** : http://localhost:8000/doc/
- **📄 Documentation lisible (ReDoc)** : http://localhost:8000/redoc/
- **🔧 Schéma JSON** : http://localhost:8000/swagger.json
- **📋 Schéma YAML** : http://localhost:8000/swagger.yaml

### ✨ Fonctionnalités Swagger :
- ✅ **Interface interactive** avec formulaires de test
- ✅ **Authentification JWT intégrée** (bouton "Authorize")
- ✅ **Exemples de requêtes et réponses** complets
- ✅ **Organisation par catégories** (Authentication, Projects, Issues, Comments)
- ✅ **Test direct des routes** depuis l'interface
- ✅ **Documentation des paramètres** et codes de statut

### 🔧 Comment utiliser Swagger :
1. **Accédez à** : http://localhost:8000/doc/
2. **Authentifiez-vous** : Cliquez sur "Authorize" et saisissez votre token JWT
3. **Testez les routes** : Cliquez sur une route → "Try it out" → Saisissez les paramètres → "Execute"

### 🔑 Authentification dans Swagger :
```
Valeur à saisir dans "Authorize" : Bearer YOUR_ACCESS_TOKEN
```

## 🐳 Déploiement Docker

### Dockerfile inclus

Le projet inclut un `Dockerfile` optimisé pour un déploiement simple :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

# Copier le code source
COPY . .
WORKDIR /app/softdesk

# Exposer le port et lancer le serveur
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Commandes Docker

```bash
# Construction de l'image
docker build -t softdesk-api .

# Lancement du conteneur
docker run -d \
  --name softdesk \
  -p 8000:8000 \
  softdesk-api

# Gestion du conteneur
docker logs -f softdesk     # Voir les logs
docker stop softdesk        # Arrêter
docker start softdesk       # Redémarrer
docker rm softdesk          # Supprimer
```

### Accès aux services (Docker)

Une fois le conteneur lancé :
- **API principale** : http://localhost:8000/api/
- **Documentation Swagger** : http://localhost:8000/doc/
- **Interface Admin** : http://localhost:8000/admin/
- **Documentation ReDoc** : http://localhost:8000/redoc/

## 🛠️ Caractéristiques techniques

### Stack technologique :
- **Backend** : Django 5.2.3 + Django REST Framework
- **Authentification** : JWT (djangorestframework-simplejwt)
- **Documentation** : Swagger/OpenAPI (drf-yasg)
- **Base de données** : SQLite (développement)
- **Containerisation** : Docker

### Architecture :
- **API RESTful** avec routes hiérarchiques
- **Permissions granulaires** par rôle (Auteur/Contributeur)
- **Gestion d'UUID** pour les commentaires
- **Validation RGPD** et contrôle d'âge intégré