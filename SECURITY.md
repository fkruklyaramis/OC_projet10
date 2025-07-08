# 🔒 Politique de Sécurité - API SoftDesk

## 📋 Aperçu

L'API SoftDesk implémente les standards de sécurité les plus élevés conformément aux recommandations **OWASP Top 10** et aux exigences **RGPD/GDPR**. Cette documentation détaille toutes les mesures de sécurité mises en place.

## 🛡️ OWASP Top 10 - Mesures Implémentées

### A01 : Broken Access Control
**❌ Vulnérabilité** : Contrôles d'accès inadéquats
**✅ Protection Implémentée** :
```python
# Permissions personnalisées strictes
class IsAuthorOrContributor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Seuls les auteurs peuvent modifier/supprimer
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.author == request.user
        # Les contributeurs peuvent lire
        return obj.contributors.filter(user=request.user).exists()
```
- **JWT obligatoire** pour toutes les routes (sauf auth)
- **Permissions granulaires** par rôle (Auteur/Contributeur)
- **Validation systématique** de l'appartenance aux projets

### A02 : Cryptographic Failures
**❌ Vulnérabilité** : Chiffrement faible ou absent
**✅ Protection Implémentée** :
```python
# Hachage sécurisé des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    'django.contrib.auth.password_validation.MinimumLengthValidator',
    'django.contrib.auth.password_validation.CommonPasswordValidator',
    'django.contrib.auth.password_validation.NumericPasswordValidator',
]

# JWT avec rotation automatique
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### A03 : Injection
**❌ Vulnérabilité** : Injection SQL, XSS, Command Injection
**✅ Protection Implémentée** :
```python
# Protection XSS avec bleach
def validate_description(self, value):
    if value:
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
        cleaned_value = bleach.clean(
            value,
            tags=allowed_tags,
            strip=True,
            attributes={}
        )
        return cleaned_value

# Validation regex stricte
username = serializers.CharField(
    validators=[
        RegexValidator(
            regex=r'^[a-zA-Z0-9_-]{3,150}$',
            message="Username: 3-150 caractères alphanumériques uniquement"
        )
    ]
)
```
- **ORM Django** : Protection native contre l'injection SQL
- **Validation stricte** : Regex patterns pour tous les inputs
- **Bleach sanitization** : Nettoyage automatique du HTML

### A04 : Insecure Design
**❌ Vulnérabilité** : Architecture de sécurité insuffisante
**✅ Protection Implémentée** :
- **Principe du moindre privilège** : Accès minimal nécessaire
- **Défense en profondeur** : Plusieurs couches de sécurité
- **Fail-safe defaults** : Accès refusé par défaut

### A05 : Security Misconfiguration
**❌ Vulnérabilité** : Configuration de sécurité incorrecte
**✅ Protection Implémentée** :
```python
# Headers de sécurité obligatoires
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Production settings
SECURE_SSL_REDIRECT = True  # Force HTTPS
SECURE_HSTS_SECONDS = 31536000  # HSTS 1 an
```

### A06 : Vulnerable and Outdated Components
**❌ Vulnérabilité** : Dépendances obsolètes ou vulnérables
**✅ Protection Implémentée** :
```toml
# Pipfile - Versions spécifiques et à jour
django = "==5.2.3"
djangorestframework = "==3.16.0"
djangorestframework-simplejwt = "==5.5.0"
```
- **Pipenv** : Gestion sécurisée des dépendances
- **Versions verrouillées** : Prévention des updates automatiques
- **Audit régulier** : Surveillance des CVE

### A07 : Identification and Authentication Failures
**❌ Vulnérabilité** : Authentification faible
**✅ Protection Implémentée** :
```python
# Rate limiting strict
'DEFAULT_THROTTLE_RATES': {
    'login': '5/minute',     # Max 5 tentatives/minute
    'register': '3/hour',    # Max 3 inscriptions/heure
}

# Validation mot de passe renforcée
def validate_password(self, value):
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Majuscule requise")
    if not re.search(r'[a-z]', value):
        raise ValidationError("Minuscule requise")
    if not re.search(r'\d', value):
        raise ValidationError("Chiffre requis")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError("Caractère spécial requis")
```

### A08 : Software and Data Integrity Failures
**❌ Vulnérabilité** : Intégrité des données compromise
**✅ Protection Implémentée** :
- **JWT signés** : Vérification cryptographique de l'intégrité
- **Validation stricte** : Contrôle de tous les inputs
- **Audit trail** : Traçabilité complète des modifications

### A09 : Security Logging and Monitoring Failures
**❌ Vulnérabilité** : Logging et monitoring insuffisants
**✅ Protection Implémentée** :
```python
# Configuration logging sécurité
LOGGING = {
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api.gdpr': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Logs sécurité automatiques
security_logger.info(f"Failed login attempt for user: {username}")
gdpr_logger.info(f"Data export requested by user: {user.username}")
```

### A10 : Server-Side Request Forgery (SSRF)
**❌ Vulnérabilité** : Requêtes serveur non validées
**✅ Protection Implémentée** :
- **Pas de requêtes externes** : API fermée, pas d'endpoints SSRF
- **Validation des URLs** : Si implémentation future
- **Whitelist domains** : Contrôle strict des domaines autorisés

## 📋 Conformité RGPD/GDPR

### Principe 1 : Licéité, Loyauté, Transparence
```python
# Consentements explicites
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = [..., 'can_be_contacted', 'can_data_be_shared']
```
- **Base légale claire** : Consentement explicite pour contact/partage
- **Information transparente** : Documentation complète des traitements
- **Opt-in uniquement** : Pas de cases précochées

### Principe 2 : Limitation des Finalités
- **Finalité définie** : Gestion de projets collaboratifs uniquement
- **Pas de réutilisation** : Données non utilisées à d'autres fins
- **Traçabilité** : Logs de tous les usages des données

### Principe 3 : Minimisation des Données
```python
# Collecte minimale
fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth']
# Pas de données sensibles inutiles (race, religion, etc.)
```

### Principe 4 : Exactitude
```python
# Droit de rectification
PATCH /api/auth/profile/  # Modification des données personnelles
```

### Principe 5 : Limitation de Conservation
```python
# Politique de rétention
DATA_RETENTION_DAYS = 2555  # 7 ans (conformité légale)
```

### Principe 6 : Intégrité et Confidentialité
- **Chiffrement** : HTTPS obligatoire, mots de passe hashés
- **Contrôle d'accès** : Permissions strictes
- **Audit** : Logs sécurisés

### Principe 7 : Responsabilité
- **Documentation complète** : Politiques et procédures écrites
- **Formation équipe** : Sensibilisation RGPD
- **Audits réguliers** : Vérification conformité

## 🔍 Droits des Utilisateurs RGPD

### Droit d'Information (Article 13-14)
- **Mention d'information** : Disponible lors de l'inscription
- **Finalités claires** : Gestion collaborative de projets
- **Durée de conservation** : 7 ans maximum

### Droit d'Accès (Article 15)
```http
GET /api/auth/profile/
# Retourne toutes les données personnelles
```

### Droit de Rectification (Article 16)
```http
PATCH /api/auth/profile/
{
    "first_name": "Nouveau prénom",
    "email": "nouvel@email.com"
}
```

### Droit à l'Effacement (Article 17)
```http
DELETE /api/auth/gdpr/delete/
# Suppression définitive et irréversible
```

### Droit à la Portabilité (Article 20)
```http
GET /api/auth/gdpr/export/
# Export JSON de toutes les données
```

### Droit d'Opposition (Article 21)
```http
PATCH /api/auth/profile/
{
    "can_be_contacted": false,
    "can_data_be_shared": false
}
```

## 🚨 Signalement de Vulnérabilités

### Responsible Disclosure Policy

#### 1. Découverte d'une Vulnérabilité
- **Ne pas exploiter** la vulnérabilité
- **Ne pas accéder** aux données d'autres utilisateurs
- **Ne pas divulguer publiquement** avant correction

#### 2. Signalement
**Email** : security@softdesk.com
**Format requis** :
```
Objet: [SECURITY] Vulnérabilité - [Niveau de gravité]

Description:
- Type de vulnérabilité
- Steps to reproduce
- Impact potentiel
- Preuves de concept (si applicable)

Contact:
- Nom/Pseudo
- Email de contact
- Coordonnées (optionnel)
```

#### 3. Processus de Traitement
1. **Accusé de réception** : Dans les 24h
2. **Évaluation initiale** : Dans les 48h
3. **Correction** : Selon gravité (24h à 30 jours)
4. **Notification** : Mise à jour du reporter
5. **Publication** : Advisory de sécurité si applicable

#### 4. Récompenses
- **Reconnaissance publique** (si souhaité)
- **Mention dans les crédits** de sécurité
- **Certificat de reconnaissance** pour contributions majeures

## 🔧 Configuration de Sécurité

### Environnement de Développement
```python
# settings/development.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOW_ALL_ORIGINS = True  # Développement uniquement

# Rate limiting plus permissif
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',
    'user': '10000/hour',
}
```

### Environnement de Production
```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = ['https://your-frontend.com']

# HTTPS obligatoire
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Base de données sécurisée
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

## 📊 Tests de Sécurité

### Tests Automatisés
```python
# tests/test_security.py
class SecurityTestCase(TestCase):
    
    def test_password_strength(self):
        """Test validation mot de passe fort"""
        weak_passwords = ['123', 'password', 'abcdefgh']
        for pwd in weak_passwords:
            with self.assertRaises(ValidationError):
                validate_password_strength(pwd)
    
    def test_xss_protection(self):
        """Test protection XSS"""
        malicious_input = '<script>alert("XSS")</script>'
        cleaned = bleach.clean(malicious_input, tags=[], strip=True)
        self.assertEqual(cleaned, 'alert("XSS")')
    
    def test_rate_limiting(self):
        """Test limitation de taux"""
        # Simulation d'attaque par force brute
        for i in range(10):
            response = self.client.post('/api/auth/login/', {
                'username': 'test', 'password': 'wrong'
            })
        self.assertEqual(response.status_code, 429)  # Too Many Requests
```

### Tests Manuels
1. **Injection SQL** : Tentatives d'injection dans tous les champs
2. **XSS** : Scripts malveillants dans les inputs
3. **CSRF** : Requêtes cross-site
4. **Rate Limiting** : Tests de charge sur les endpoints sensibles
5. **Permissions** : Tentatives d'accès non autorisé

## 📈 Monitoring et Alertes

### Métriques de Sécurité
```python
# Indicateurs surveillés
- Tentatives de connexion échouées par IP
- Requêtes avec rate limiting dépassé
- Accès à des ressources interdites
- Temps de réponse anormaux
- Patterns d'attaque (SQL injection, XSS)
```

### Alertes Automatiques
```bash
# Exemples d'alertes
[CRITICAL] Plus de 10 tentatives de connexion échouées depuis IP 192.168.1.100
[WARNING] Rate limiting dépassé pour l'endpoint /api/auth/login/
[INFO] Nouveau compte créé avec âge < 15 ans (auto-rejeté)
[SECURITY] Tentative d'accès non autorisé au projet #123 par user:alice
```

### Dashboard de Sécurité
- **Grafana** : Visualisation des métriques
- **Elasticsearch** : Indexation des logs
- **Kibana** : Analyse des patterns d'attaque
- **Prometheus** : Monitoring des performances

## 🛠️ Maintenance de Sécurité

### Mises à Jour Régulières
```bash
# Vérification mensuelle des dépendances
pipenv check
pipenv update

# Audit de sécurité
python -m pip install safety
safety check
```

### Revue de Code Sécurité
- **Analyse statique** : Bandit, SonarQube
- **Revue manuelle** : Focus sur les aspects sécurité
- **Tests de pénétration** : Trimestriels

### Documentation
- **Mise à jour** : À chaque modification sécuritaire
- **Formation équipe** : Sessions sécurité régulières
- **Veille technologique** : Suivi des CVE et vulnérabilités

---

**Version du document** : 1.0  
**Dernière mise à jour** : 6 juillet 2025  
**Prochaine révision** : 6 octobre 2025  

*Cette politique de sécurité est revue et mise à jour trimestriellement pour garantir la conformité aux derniers standards de sécurité.*
