# Utilise une image officielle Python légère
FROM python:3.11-slim

# Définit le dossier de travail dans le conteneur
WORKDIR /app

# Copie et installe les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code source et les données dans le conteneur
COPY src/ ./src/
COPY data/ ./data/

# Commande par défaut : lance la migration puis les tests d'intégrité
CMD ["sh", "-c", "python src/migrate.py && pytest src/test_migration.py"]