# API SoftDesk - Documentation des Routes

## � Installation et Démarrage

### Option 1 : Installation locale avec Pipenv

```bash
# Cloner le projet
git clone https://github.com/fkruklyaramis/OC_projet10.git
cd OC_projet10

# Installer les dépendances
pipenv install

# Activer l'environnement virtuel
pipenv shell

# Configurer les variables d'environnement
cp .env.example .env

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
# Cloner le projet
git clone https://github.com/fkruklyaramis/OC_projet10.git
cd OC_projet10

# Configurer les variables d'environnement
cp .env.example .env

# Construire l'image Docker
docker build -t softdesk-api .

# Lancer le conteneur
docker run -d --name softdesk -p 8000:8000 softdesk-api

# Voir les logs (optionnel)
docker logs -f softdesk

# Arrêter le conteneur
docker stop softdesk
```

# ⚙️ Configuration

### Variables d'environnement requises

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```bash
# .env
# SÉCURITÉ : Clé secrète Django (OBLIGATOIRE)
DJANGO_SECRET_KEY=votre-cle-secrete-super-longue-et-complexe-ici

# DÉVELOPPEMENT : Mode debug (optionnel)
DJANGO_DEBUG=True

# PRODUCTION : Hosts autorisés (optionnel)
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### 🔐 Génération d'une SECRET_KEY sécurisée

**Méthode recommandée :**
```bash
# Activer votre environnement virtuel puis :
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Exemple de SECRET_KEY générée :**
```
k2#f@9x$m8n&q4w5e6r7t8y9u0i1o2p3a4s5d6f7g8h9j0k1l2z3x4c5v6b7n8m9
```

### 📋 Fichier `.env.example` 

Le projet inclut un fichier `.env.example` avec toutes les variables nécessaires :

```bash
# Variables d'environnement pour SoftDesk API

# SÉCURITÉ (OBLIGATOIRE en production)
DJANGO_SECRET_KEY=changez-cette-cle-en-production

# DÉVELOPPEMENT
DJANGO_DEBUG=True

# PRODUCTION 
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

### ⚠️ Important - Sécurité

- ✅ **Copiez** `.env.example` vers `.env`
- ✅ **Modifiez** `DJANGO_SECRET_KEY` avec une clé unique
- ✅ **N'exposez jamais** votre fichier `.env` (déjà dans `.gitignore`)
- ✅ **Utilisez** `DJANGO_DEBUG=False` en production

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
| PUT | `/api/projects/{id}/issues/{issue_id}/` | Modifier complètement une issue (tous les champs requis) | Auteur issue/projet |
| PATCH | `/api/projects/{id}/issues/{issue_id}/` | Modifier partiellement une issue (champs optionnels) | Auteur issue/projet |
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

## Routes RGPD (Conformité GDPR)
| Méthode | URL | Description | Permissions |
|---------|-----|-------------|-------------|
| GET | `/api/gdpr/export-my-data/` | Exporter toutes mes données personnelles (Article 15) | Utilisateur authentifié |
| DELETE | `/api/gdpr/delete-my-account/` | Supprimer définitivement mon compte (Article 17) | Utilisateur authentifié |


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

### 9. Modifier une issue (PATCH - partiel)
```http
PATCH /api/projects/1/issues/1/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "status": "IN_PROGRESS",
    "assignee_username": "alice"
}
```

### 9bis. Modifier une issue (PUT - complet)
```http
PUT /api/projects/1/issues/1/
Content-Type: application/json
Authorization: Bearer YOUR_ACCESS_TOKEN

{
    "name": "Corriger le bug de connexion - MISE À JOUR",
    "description": "Le système de connexion ne fonctionne pas correctement. Ajout de détails.",
    "assignee_username": "alice",
    "priority": "HIGH",
    "tag": "BUG",
    "status": "IN_PROGRESS"
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

## Exemples RGPD (Conformité GDPR)

### 15. Exporter mes données personnelles (RGPD Article 15)
```http
GET /api/gdpr/export-my-data/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 16. Supprimer définitivement mon compte (RGPD Article 17)
```http
DELETE /api/gdpr/delete-my-account/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**⚠️ ATTENTION :** Cette action est **irréversible** ! Toutes vos données personnelles seront définitivement supprimées ainsi que tous vos projets, issues et commentaires créés.

## Authentification JWT

Toutes les routes (sauf auth) nécessitent un token JWT dans le header :
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 🔄 Différences PUT vs PATCH

### PUT (Remplacement complet)
- **Remplace entièrement** la ressource
- **Tous les champs** doivent être fournis
- Les champs omis sont réinitialisés à leur valeur par défaut
- Utilisation : mise à jour complète d'un objet

### PATCH (Modification partielle)  
- **Modifie seulement** les champs fournis
- Les champs non fournis **restent inchangés**
- Plus efficace pour des modifications ciblées
- Utilisation : changement de statut, assignation, etc.

**Exemple pratique :**
- **PATCH** : Changer juste le statut → `{"status": "IN_PROGRESS"}`
- **PUT** : Fournir tous les champs → `{"name": "...", "description": "...", "status": "IN_PROGRESS", ...}`

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

### Règles RGPD :
- **Droit d'accès (Article 15)** : Export complet des données personnelles
- **Droit à l'oubli (Article 17)** : Suppression définitive et anonymisation
- **Âge minimum** : 15 ans minimum pour créer un compte (contrôle automatique)
- **Consentements** : Acceptation explicite pour contact et partage de données
- **Anonymisation** : Suppression complète des données pour préserver l'intégrité de la base de données

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

Le projet inclut un Dockerfile optimisé pour un déploiement simple.

**📄 Voir le fichier complet :** [`Dockerfile`](./Dockerfile)


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
![Static Badge](https://img.shields.io/badge/python-3.12-green?style=for-the-badge)

![Static Badge](https://img.shields.io/badge/Django-5.2.3-blue?style=for-the-badge)

![Static Badge](https://img.shields.io/badge/Django-%20REST_Framework-white?style=for-the-badge)

![Static Badge](https://img.shields.io/badge/Authentification%20-%20JWT-yellow?style=for-the-badge)

![Static Badge](https://img.shields.io/badge/Documentation-Swagger%2FOpenAPI-fa89cb?style=for-the-badge)

![Static Badge](https://img.shields.io/badge/Base%20de%20donn%C3%A9es-SQLite-b2eddc?style=for-the-badge)

![Static Badge](https://img.shields.io/badge/Containerisation-Docker-ffefa6?style=for-the-badge)



### Architecture :
- **API RESTful** avec routes hiérarchiques
- **Permissions granulaires** par rôle (Auteur/Contributeur)
- **Gestion d'UUID** pour les commentaires
- **Validation RGPD** et contrôle d'âge intégré