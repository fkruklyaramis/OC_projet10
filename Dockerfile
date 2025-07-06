FROM python:3.12-slim

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY Pipfile Pipfile.lock ./

# Installer pipenv et les dépendances
RUN pip install pipenv && pipenv install --system --deploy

# Copier le code source
COPY . .

# Changer vers le répertoire Django
WORKDIR /app/softdesk

# Exposer le port
EXPOSE 8000

# Lancer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]