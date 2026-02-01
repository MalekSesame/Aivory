# Utiliser une image Python officielle
FROM python:3.11-slim

# Variables d'environnement pour Python
ENV PYTHONUNBUFFERED=1

# Créer le dossier de l'application
WORKDIR /app

# Copier les fichiers requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copier tout le code source
COPY . .

# Exposer les ports nécessaires
# FastAPI par défaut 8000, Streamlit 8501
EXPOSE 8000 8501

# Commande par défaut pour lancer l'application FastAPI
CMD ["streamlit", "run", "frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
